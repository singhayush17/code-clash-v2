# Code Clash Low-Level Design

## File Map

- `app/main.py`
  - FastAPI application setup.
  - Static file routes.
  - `/ws` WebSocket endpoint.
  - `/api/health` and `/api/admin/reload-questions`.

- `app/game.py`
  - In-memory game state and WebSocket protocol handling.
  - Room lifecycle, matchmaking, scoring, timers, and answer review.

- `app/question_bank.py`
  - JSON validation.
  - Question picking by difficulty.
  - Public question serialization.

- `data/questions.json`
  - Updateable MCQ bank.

- `web/app.js`
  - Browser state machine and WebSocket client.
  - Lobby, duration picker, battle arena, result, and current-round review UI.

- `web/styles.css`
  - Responsive UI styling.

## Core Constants

`app/game.py` defines:

- `DEFAULT_GAME_SECONDS = 60`
- `ALLOWED_GAME_SECONDS = (30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600)`
- `INVITE_TTL_SECONDS = 30 * 60`
- `ENDED_ROOM_TTL_SECONDS = 75`

Any duration received from the client is validated by `_duration_from_payload`. Invalid or missing values fall back to 60 seconds.

## Data Models

### Connection

Represents one active WebSocket.

Fields:

- `id`: connection id.
- `player_id`: transient player id for this socket session.
- `username`: generated username.
- `avatar`: generated avatar descriptor.
- `room_id`: current room, if any.
- `queued`: whether the connection is in matchmaking.
- `queued_duration_seconds`: selected duration for matchmaking.

### PlayerState

Represents a player inside one room.

Fields:

- `score`: correct answer count.
- `answered`: number of submitted answers.
- `streak`: current correct-answer streak.
- `current_question_id`: server-side guard against answering stale questions.
- `asked_ids`: question ids already asked to this player in this room.
- `answer_history`: current-game review items.

`answer_history` is cleared in `reset_for_game` and is never written to disk.

### Room

Represents a waiting, active, or ended room.

Fields:

- `id`: shareable room code.
- `mode`: `invite`, `matchmaking`, or `solo`.
- `owner_id`: creator or first matched player.
- `duration_seconds`: selected battle duration.
- `expires_at`: waiting-room expiry timestamp.
- `status`: `waiting`, `active`, or `ended`.
- `players`: transient player states.
- `started_at`, `ends_at`, `ended_at`: timer state.
- `end_task`: asyncio task that ends the match.

## WebSocket Protocol

### Server To Client

`hello`

```json
{
  "type": "hello",
  "player": {},
  "bank": {},
  "durations": [30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600],
  "defaultDurationSeconds": 60,
  "serverNow": 0
}
```

`room_created`

```json
{
  "type": "room_created",
  "room": {},
  "sharePath": "/room/ABC123",
  "serverNow": 0
}
```

`queued`

```json
{
  "type": "queued",
  "durationSeconds": 120
}
```

`game_started`

```json
{
  "type": "game_started",
  "room": {},
  "durationSeconds": 120,
  "serverNow": 0
}
```

`question`

```json
{
  "type": "question",
  "question": {
    "id": "dsa-e-001",
    "category": "DSA",
    "difficulty": "easy",
    "prompt": "Question text",
    "options": ["A", "B", "C", "D"]
  },
  "targetDifficulty": "easy",
  "serverNow": 0,
  "endsAt": 0
}
```

`answer_result`

```json
{
  "type": "answer_result",
  "correct": true,
  "correctIndex": 0,
  "score": 3,
  "streak": 2,
  "explanation": "Short explanation"
}
```

`game_over`

```json
{
  "type": "game_over",
  "room": {},
  "winnerId": "player-id-or-null",
  "isTie": false,
  "review": [
    {
      "question": {},
      "selectedIndex": 1,
      "correctIndex": 0,
      "correct": false,
      "explanation": "Short explanation",
      "answeredAt": 0
    }
  ]
}
```

`review` is customized per player.

### Client To Server

Create invite room:

```json
{
  "type": "create_room",
  "durationSeconds": 120
}
```

Join invite room:

```json
{
  "type": "join_room",
  "roomId": "ABC123"
}
```

Join matchmaking:

```json
{
  "type": "join_matchmaking",
  "durationSeconds": 120
}
```

Play solo:

```json
{
  "type": "play_solo",
  "durationSeconds": 120
}
```

Submit answer:

```json
{
  "type": "answer",
  "questionId": "dsa-e-001",
  "optionIndex": 0
}
```

## Room Lifecycle

1. Waiting
   - Invite room is created with a selected duration.
   - Room can accept one opponent until full, expired, or abandoned.

2. Active
   - Starts when invite room has 2 players, matchmaking finds a pair, or solo starts.
   - `started_at` and `ends_at` are set by the server.
   - Each player receives a separate question stream.
   - Each answer is validated against `current_question_id`.

3. Ended
   - Triggered by the room timer.
   - Winner is calculated from score.
   - Server sends final scoreboard plus per-player review.
   - Cleanup removes ended rooms after `ENDED_ROOM_TTL_SECONDS`.

## Difficulty Selection

The current adaptive rules are intentionally simple:

- Hard if score is at least 8, answered count is at least 10, or streak is at least 5.
- Medium if score is at least 4, answered count is at least 5, or streak is at least 3.
- Easy otherwise.

Question picking tries the target difficulty first and avoids repeats for the player. If that pool is exhausted, it falls back to unseen questions from any difficulty. If the player has seen everything, the seen set is cleared.

## Matchmaking

The queue stores connection ids. Each queued connection also stores `queued_duration_seconds`.

When a player joins matchmaking:

1. The server validates the requested duration.
2. The server scans the queue for the first active connection with the same duration.
3. If found, it creates a matchmaking room with that duration.
4. If not found, it queues the player under that duration.

This keeps expectations aligned for match length without adding profiles or ranking.

## Current-Game Review

On each answer, the server appends one review item to `PlayerState.answer_history`:

- Public question data.
- Selected option index.
- Correct option index.
- Correctness boolean.
- Explanation.
- Answer timestamp.

At game over, each connected player receives only their own `answer_history`. The browser stores it in memory as `state.roundReview` and renders it when the player clicks `Review Answers`.

The review is not persisted. It disappears when the browser refreshes, the room is cleaned up, or the server restarts.

## Failure Behavior

- If a player disconnects before a waiting invite starts, they are removed from that room.
- If all players disconnect during an active room, the room is deleted.
- If one player disconnects during an active 1v1, the other player can continue until time ends.
- If a server restarts, all rooms, queues, scores, and current reviews are lost by design.
