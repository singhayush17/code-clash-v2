from __future__ import annotations

import asyncio
import secrets
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from .question_bank import QuestionBank, public_question


DEFAULT_GAME_SECONDS = 60
ALLOWED_GAME_SECONDS = (30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600)
INVITE_TTL_SECONDS = 30 * 60
ENDED_ROOM_TTL_SECONDS = 75
ROOM_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

ADJECTIVES = [
    "Agile",
    "Bright",
    "Calm",
    "Clever",
    "Daring",
    "Electric",
    "Fast",
    "Keen",
    "Logic",
    "Neon",
    "Prime",
    "Quick",
    "Sharp",
    "Swift",
    "Vector",
]

NOUNS = [
    "Array",
    "Bit",
    "Cache",
    "Cursor",
    "Graph",
    "Heap",
    "Kernel",
    "Lambda",
    "Packet",
    "Pivot",
    "Queue",
    "Stack",
    "Thread",
    "Trie",
    "Vertex",
]

AVATAR_PALETTES = [
    ("#00a676", "#111111", "#ffc857"),
    ("#ff5a5f", "#111111", "#2ec4b6"),
    ("#2ec4b6", "#111111", "#ff5a5f"),
    ("#ffc857", "#111111", "#00a676"),
    ("#7bd389", "#111111", "#ff5a5f"),
    ("#ff8c42", "#111111", "#2ec4b6"),
]


def now_ms() -> int:
    return int(time.time() * 1000)


def room_code() -> str:
    return "".join(secrets.choice(ROOM_ALPHABET) for _ in range(6))


def player_id() -> str:
    return secrets.token_urlsafe(9)


def random_name() -> str:
    return f"{secrets.choice(ADJECTIVES)} {secrets.choice(NOUNS)}"


def random_avatar() -> dict[str, str]:
    bg, ink, accent = secrets.choice(AVATAR_PALETTES)
    return {
        "bg": bg,
        "ink": ink,
        "accent": accent,
        "shape": secrets.choice(["bolt", "rings", "grid", "orbit"]),
    }


@dataclass
class Connection:
    id: str
    websocket: WebSocket
    player_id: str
    username: str
    avatar: dict[str, str]
    room_id: str | None = None
    queued: bool = False
    queued_duration_seconds: int | None = None


@dataclass
class PlayerState:
    id: str
    username: str
    avatar: dict[str, str]
    score: int = 0
    answered: int = 0
    streak: int = 0
    connected: bool = True
    current_question_id: str | None = None
    asked_ids: set[str] = field(default_factory=set)
    answer_history: list[dict[str, Any]] = field(default_factory=list)

    def reset_for_game(self) -> None:
        self.score = 0
        self.answered = 0
        self.streak = 0
        self.connected = True
        self.current_question_id = None
        self.asked_ids.clear()
        self.answer_history.clear()

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "avatar": self.avatar,
            "score": self.score,
            "answered": self.answered,
            "streak": self.streak,
            "connected": self.connected,
        }


@dataclass
class Room:
    id: str
    mode: str
    owner_id: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + INVITE_TTL_SECONDS)
    duration_seconds: int = DEFAULT_GAME_SECONDS
    status: str = "waiting"
    players: dict[str, PlayerState] = field(default_factory=dict)
    started_at: float | None = None
    ends_at: float | None = None
    ended_at: float | None = None
    end_task: asyncio.Task[None] | None = None

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "mode": self.mode,
            "status": self.status,
            "players": [player.public() for player in self.players.values()],
            "durationSeconds": self.duration_seconds,
            "createdAt": int(self.created_at * 1000),
            "expiresAt": int(self.expires_at * 1000),
            "startedAt": int(self.started_at * 1000) if self.started_at else None,
            "endsAt": int(self.ends_at * 1000) if self.ends_at else None,
        }


class GameManager:
    def __init__(self, question_bank: QuestionBank) -> None:
        self.question_bank = question_bank
        self.connections: dict[str, Connection] = {}
        self.rooms: dict[str, Room] = {}
        self.queue: deque[str] = deque()
        self._cleanup_task: asyncio.Task[None] | None = None

    def start_cleanup(self) -> None:
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def register(self, websocket: WebSocket) -> Connection:
        await websocket.accept()
        conn = Connection(
            id=player_id(),
            websocket=websocket,
            player_id=player_id(),
            username=random_name(),
            avatar=random_avatar(),
        )
        self.connections[conn.id] = conn
        await self.send(
            conn,
            {
                "type": "hello",
                "player": {
                    "id": conn.player_id,
                    "username": conn.username,
                    "avatar": conn.avatar,
                },
                "bank": self.question_bank.stats(),
                "durations": list(ALLOWED_GAME_SECONDS),
                "defaultDurationSeconds": DEFAULT_GAME_SECONDS,
                "serverNow": now_ms(),
            },
        )
        return conn

    async def disconnect(self, conn: Connection) -> None:
        self.connections.pop(conn.id, None)
        self._remove_from_queue(conn)

        if not conn.room_id:
            return

        room = self.rooms.get(conn.room_id)
        if not room:
            return

        player = room.players.get(conn.player_id)
        if player:
            player.connected = False

        if room.status == "waiting":
            room.players.pop(conn.player_id, None)
            if not room.players:
                self._delete_room(room.id)
            else:
                await self.broadcast_room(room, {"type": "room_update", "room": room.public()})
            return

        await self.broadcast_scoreboard(room)

        if room.status == "active" and all(
            not player.connected for player in room.players.values()
        ):
            self._delete_room(room.id)

    async def handle(self, conn: Connection, payload: dict[str, Any]) -> None:
        message_type = payload.get("type")

        if message_type == "create_room":
            await self.create_invite_room(
                conn, self._duration_from_payload(payload.get("durationSeconds"))
            )
        elif message_type == "join_room":
            await self.join_invite_room(conn, str(payload.get("roomId", "")))
        elif message_type == "join_matchmaking":
            await self.join_matchmaking(
                conn, self._duration_from_payload(payload.get("durationSeconds"))
            )
        elif message_type == "leave_queue":
            self._remove_from_queue(conn)
            await self.send(conn, {"type": "queue_left"})
        elif message_type == "leave_room":
            await self.leave_room(conn)
        elif message_type == "play_solo":
            await self.play_solo(
                conn, self._duration_from_payload(payload.get("durationSeconds"))
            )
        elif message_type == "answer":
            await self.answer(
                conn,
                str(payload.get("questionId", "")),
                payload.get("optionIndex"),
            )
        else:
            await self.send_error(conn, "Unknown action.")

    async def create_invite_room(self, conn: Connection, duration_seconds: int) -> None:
        if not await self._can_start_new_activity(conn):
            return

        self._leave_current_room(conn)
        self._remove_from_queue(conn)

        code = self._unique_room_code()
        room = Room(
            id=code,
            mode="invite",
            owner_id=conn.player_id,
            duration_seconds=duration_seconds,
        )
        room.players[conn.player_id] = self._player_from_connection(conn)
        conn.room_id = room.id
        self.rooms[room.id] = room

        await self.send(
            conn,
            {
                "type": "room_created",
                "room": room.public(),
                "sharePath": f"/room/{room.id}",
                "serverNow": now_ms(),
            },
        )

    async def join_invite_room(self, conn: Connection, requested_room_id: str) -> None:
        if not await self._can_start_new_activity(conn):
            return

        code = "".join(
            char for char in requested_room_id.strip().upper() if char in ROOM_ALPHABET
        )
        room = self.rooms.get(code)

        if not room:
            await self.send_error(conn, "That battle link is invalid or already gone.")
            return

        if time.time() > room.expires_at:
            await self._expire_room(room)
            await self.send_error(conn, "That battle link expired after 30 minutes.")
            return

        if room.mode != "invite" or room.status != "waiting":
            await self.send_error(conn, "That battle is no longer joinable.")
            return

        if len(room.players) >= 2 and conn.player_id not in room.players:
            await self.send_error(conn, "That battle room is full.")
            return

        if conn.room_id == room.id and conn.player_id in room.players:
            await self.send(conn, {"type": "room_update", "room": room.public()})
            return

        self._leave_current_room(conn)
        self._remove_from_queue(conn)
        room.players[conn.player_id] = self._player_from_connection(conn)
        conn.room_id = room.id

        await self.broadcast_room(room, {"type": "room_update", "room": room.public()})

        if len(room.players) == 2:
            await self.start_game(room)

    async def join_matchmaking(self, conn: Connection, duration_seconds: int) -> None:
        if not await self._can_start_new_activity(conn):
            return

        self._leave_current_room(conn)

        if conn.queued:
            await self.send(
                conn,
                {
                    "type": "queued",
                    "durationSeconds": conn.queued_duration_seconds
                    or duration_seconds,
                },
            )
            return

        opponent = self._next_waiting_opponent(conn, duration_seconds)
        if opponent is None:
            conn.queued = True
            conn.queued_duration_seconds = duration_seconds
            self.queue.append(conn.id)
            await self.send(
                conn, {"type": "queued", "durationSeconds": duration_seconds}
            )
            return

        code = self._unique_room_code()
        room = Room(
            id=code,
            mode="matchmaking",
            owner_id=opponent.player_id,
            duration_seconds=duration_seconds,
        )
        room.players[opponent.player_id] = self._player_from_connection(opponent)
        room.players[conn.player_id] = self._player_from_connection(conn)
        opponent.room_id = room.id
        conn.room_id = room.id
        self.rooms[room.id] = room
        await self.start_game(room)

    async def leave_room(self, conn: Connection) -> None:
        room = self.rooms.get(conn.room_id or "")
        if room and room.status == "active":
            await self.send_error(conn, "Finish the current battle first.")
            return

        previous_room = self._leave_current_room(conn)
        await self.send(conn, {"type": "left_room"})

        if previous_room and previous_room.id in self.rooms:
            await self.broadcast_room(
                previous_room,
                {"type": "room_update", "room": previous_room.public()},
            )

    async def play_solo(self, conn: Connection, duration_seconds: int) -> None:
        if not await self._can_start_new_activity(conn):
            return

        self._leave_current_room(conn)
        self._remove_from_queue(conn)

        code = self._unique_room_code()
        room = Room(
            id=code,
            mode="solo",
            owner_id=conn.player_id,
            duration_seconds=duration_seconds,
        )
        room.players[conn.player_id] = self._player_from_connection(conn)
        conn.room_id = room.id
        self.rooms[room.id] = room
        await self.start_game(room)

    async def answer(
        self, conn: Connection, question_id: str, option_index: Any
    ) -> None:
        room = self.rooms.get(conn.room_id or "")
        if not room or room.status != "active":
            await self.send_error(conn, "No active battle.")
            return

        if room.ends_at is None or time.time() >= room.ends_at:
            await self.finish_game(room.id, "time")
            return

        player = room.players.get(conn.player_id)
        if not player:
            await self.send_error(conn, "You are not in this battle.")
            return

        if player.current_question_id != question_id:
            await self.send_error(conn, "That question is no longer active.")
            return

        if not isinstance(option_index, int) or option_index not in range(4):
            await self.send_error(conn, "Pick one of the four options.")
            return

        question = self.question_bank.get(question_id)
        if not question:
            await self.send_error(conn, "That question was removed from the bank.")
            return

        player.current_question_id = None
        correct = question["answerIndex"] == option_index
        player.answered += 1

        if correct:
            player.score += 1
            player.streak += 1
        else:
            player.streak = 0

        player.answer_history.append(
            {
                "question": public_question(question),
                "selectedIndex": option_index,
                "correctIndex": question["answerIndex"],
                "correct": correct,
                "explanation": question.get("explanation", ""),
                "answeredAt": now_ms(),
            }
        )

        await self.send(
            conn,
            {
                "type": "answer_result",
                "correct": correct,
                "correctIndex": question["answerIndex"],
                "score": player.score,
                "streak": player.streak,
                "explanation": question.get("explanation", ""),
            },
        )
        await self.broadcast_scoreboard(room)

        if room.status == "active" and room.ends_at and time.time() < room.ends_at:
            await self.send_next_question(conn, room, player)

    async def reload_questions(self) -> dict[str, Any]:
        stats = self.question_bank.load()
        return stats

    async def start_game(self, room: Room) -> None:
        room.status = "active"
        room.started_at = time.time()
        room.ends_at = room.started_at + room.duration_seconds

        for player in room.players.values():
            player.reset_for_game()

        await self.broadcast_room(
            room,
            {
                "type": "game_started",
                "room": room.public(),
                "durationSeconds": room.duration_seconds,
                "serverNow": now_ms(),
            },
        )
        await self.broadcast_scoreboard(room)

        for player in list(room.players.values()):
            conn = self._connection_for_player(player.id)
            if conn:
                await self.send_next_question(conn, room, player)

        room.end_task = asyncio.create_task(
            self._finish_after(room.id, room.duration_seconds)
        )

    async def send_next_question(
        self, conn: Connection, room: Room, player: PlayerState
    ) -> None:
        difficulty = self._target_difficulty(player)
        question = self.question_bank.pick(difficulty, player.asked_ids)
        player.current_question_id = question["id"]
        player.asked_ids.add(question["id"])

        await self.send(
            conn,
            {
                "type": "question",
                "question": public_question(question),
                "targetDifficulty": difficulty,
                "serverNow": now_ms(),
                "endsAt": int((room.ends_at or time.time()) * 1000),
            },
        )

    async def finish_game(self, room_id: str, reason: str) -> None:
        room = self.rooms.get(room_id)
        if not room or room.status == "ended":
            return

        room.status = "ended"
        room.ended_at = time.time()

        players = list(room.players.values())
        top_score = max((player.score for player in players), default=0)
        leaders = [player for player in players if player.score == top_score]
        winner_id = leaders[0].id if len(leaders) == 1 else None

        base_payload = {
            "type": "game_over",
            "reason": reason,
            "room": room.public(),
            "winnerId": winner_id,
            "isTie": len(leaders) > 1 and len(players) > 1,
            "serverNow": now_ms(),
        }

        for player in players:
            conn = self._connection_for_player(player.id)
            if conn:
                await self.send(
                    conn,
                    {
                        **base_payload,
                        "review": player.answer_history,
                    },
                )

    async def broadcast_scoreboard(self, room: Room) -> None:
        remaining_ms = 0
        if room.status == "active" and room.ends_at:
            remaining_ms = max(0, int((room.ends_at - time.time()) * 1000))

        await self.broadcast_room(
            room,
            {
                "type": "scoreboard",
                "players": [player.public() for player in room.players.values()],
                "remainingMs": remaining_ms,
                "serverNow": now_ms(),
            },
        )

    async def broadcast_room(self, room: Room, payload: dict[str, Any]) -> None:
        for player in list(room.players.values()):
            conn = self._connection_for_player(player.id)
            if conn:
                await self.send(conn, payload)

    async def send(self, conn: Connection, payload: dict[str, Any]) -> None:
        try:
            await conn.websocket.send_json(payload)
        except RuntimeError:
            self.connections.pop(conn.id, None)

    async def send_error(self, conn: Connection, message: str) -> None:
        await self.send(conn, {"type": "error", "message": message})

    async def _can_start_new_activity(self, conn: Connection) -> bool:
        room = self.rooms.get(conn.room_id or "")
        if room and room.status == "active":
            await self.send_error(conn, "Finish the current battle first.")
            return False
        return True

    def _duration_from_payload(self, value: Any) -> int:
        try:
            duration_seconds = int(value)
        except (TypeError, ValueError):
            return DEFAULT_GAME_SECONDS

        if duration_seconds in ALLOWED_GAME_SECONDS:
            return duration_seconds
        return DEFAULT_GAME_SECONDS

    def _leave_current_room(self, conn: Connection) -> Room | None:
        room = self.rooms.get(conn.room_id or "")
        if not room or room.status == "active":
            return None

        room.players.pop(conn.player_id, None)
        conn.room_id = None

        if not room.players:
            self._delete_room(room.id)

        return room

    def _remove_from_queue(self, conn: Connection) -> None:
        conn.queued = False
        conn.queued_duration_seconds = None
        self.queue = deque(
            queued_conn_id
            for queued_conn_id in self.queue
            if queued_conn_id != conn.id
        )

    def _next_waiting_opponent(
        self, conn: Connection, duration_seconds: int
    ) -> Connection | None:
        self._remove_from_queue(conn)
        remaining: deque[str] = deque()
        opponent: Connection | None = None

        while self.queue:
            queued_conn_id = self.queue.popleft()
            candidate = self.connections.get(queued_conn_id)
            if (
                opponent is None
                and candidate
                and candidate.id != conn.id
                and candidate.queued
                and candidate.queued_duration_seconds == duration_seconds
            ):
                candidate.queued = False
                candidate.queued_duration_seconds = None
                opponent = candidate
                continue

            if candidate and candidate.queued:
                remaining.append(queued_conn_id)

        self.queue = remaining
        return opponent

    def _player_from_connection(self, conn: Connection) -> PlayerState:
        return PlayerState(
            id=conn.player_id,
            username=conn.username,
            avatar=conn.avatar,
            connected=True,
        )

    def _connection_for_player(self, player_id_value: str) -> Connection | None:
        return next(
            (
                conn
                for conn in self.connections.values()
                if conn.player_id == player_id_value
            ),
            None,
        )

    def _target_difficulty(self, player: PlayerState) -> str:
        if player.score >= 8 or player.answered >= 10 or player.streak >= 5:
            return "hard"
        if player.score >= 4 or player.answered >= 5 or player.streak >= 3:
            return "medium"
        return "easy"

    def _unique_room_code(self) -> str:
        code = room_code()
        while code in self.rooms:
            code = room_code()
        return code

    async def _finish_after(self, room_id: str, delay_seconds: int) -> None:
        await asyncio.sleep(delay_seconds)
        await self.finish_game(room_id, "time")

    async def _expire_room(self, room: Room) -> None:
        if room.status != "waiting":
            return

        await self.broadcast_room(
            room,
            {
                "type": "room_expired",
                "message": "This share link expired after 30 minutes.",
            },
        )
        self._delete_room(room.id)

    def _delete_room(self, room_id: str) -> None:
        room = self.rooms.pop(room_id, None)
        if not room:
            return

        if room.end_task and not room.end_task.done():
            room.end_task.cancel()

        for conn in self.connections.values():
            if conn.room_id == room_id:
                conn.room_id = None

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(15)
            current_time = time.time()
            for room in list(self.rooms.values()):
                if room.status == "waiting" and current_time > room.expires_at:
                    await self._expire_room(room)
                elif (
                    room.status == "ended"
                    and room.ended_at
                    and current_time - room.ended_at > ENDED_ROOM_TTL_SECONDS
                ):
                    self._delete_room(room.id)
