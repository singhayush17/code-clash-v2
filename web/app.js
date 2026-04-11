const state = {
  socket: null,
  connected: false,
  player: null,
  bank: null,
  durations: [30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600],
  durationSeconds: 60,
  queuedDurationSeconds: null,
  room: null,
  queued: false,
  question: null,
  result: null,
  roundReview: [],
  showReview: false,
  gameOver: null,
  error: "",
  shareUrl: "",
  answerLocked: false,
  serverOffsetMs: 0,
  timerId: null,
  routeRoomId: getRouteRoomId(),
};

const app = document.querySelector("#app");

function getRouteRoomId() {
  const match = window.location.pathname.match(/^\/room\/([A-Za-z0-9]+)/);
  return match ? match[1].toUpperCase() : "";
}

function wsUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

function send(type, payload = {}) {
  if (!state.socket || state.socket.readyState !== WebSocket.OPEN) {
    showError("Still connecting. Try again in a second.");
    return;
  }
  state.socket.send(JSON.stringify({ type, ...payload }));
}

function connect() {
  state.socket = new WebSocket(wsUrl());

  state.socket.addEventListener("open", () => {
    state.connected = true;
    render();
  });

  state.socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    handleMessage(message);
  });

  state.socket.addEventListener("close", () => {
    state.connected = false;
    state.queued = false;
    state.queuedDurationSeconds = null;
    state.room = null;
    state.question = null;
    state.result = null;
    state.roundReview = [];
    state.showReview = false;
    state.gameOver = null;
    state.shareUrl = "";
    state.routeRoomId = getRouteRoomId();
    stopTimer();
    render();
    setTimeout(connect, 1200);
  });
}

function handleMessage(message) {
  syncServerTime(message);

  switch (message.type) {
    case "hello":
      state.player = message.player;
      state.bank = message.bank;
      state.durations = message.durations || state.durations;
      state.durationSeconds = message.defaultDurationSeconds || state.durationSeconds;
      if (state.routeRoomId) {
        send("join_room", { roomId: state.routeRoomId });
        state.routeRoomId = "";
      }
      break;

    case "room_created":
      state.room = message.room;
      state.durationSeconds = message.room.durationSeconds || state.durationSeconds;
      state.queued = false;
      state.gameOver = null;
      state.question = null;
      state.result = null;
      state.roundReview = [];
      state.showReview = false;
      state.shareUrl = `${window.location.origin}${message.sharePath}`;
      break;

    case "room_update":
      state.room = message.room;
      state.durationSeconds = message.room.durationSeconds || state.durationSeconds;
      state.queued = false;
      state.queuedDurationSeconds = null;
      break;

    case "queued":
      state.queued = true;
      state.queuedDurationSeconds =
        message.durationSeconds || state.durationSeconds;
      state.room = null;
      state.gameOver = null;
      state.roundReview = [];
      state.showReview = false;
      break;

    case "queue_left":
      state.queued = false;
      state.queuedDurationSeconds = null;
      break;

    case "left_room":
      state.room = null;
      state.shareUrl = "";
      state.question = null;
      state.result = null;
      state.roundReview = [];
      state.showReview = false;
      state.gameOver = null;
      break;

    case "game_started":
      state.room = message.room;
      state.durationSeconds =
        message.durationSeconds || message.room.durationSeconds || state.durationSeconds;
      state.queued = false;
      state.gameOver = null;
      state.question = null;
      state.result = null;
      state.roundReview = [];
      state.showReview = false;
      state.answerLocked = false;
      startTimer();
      break;

    case "question":
      state.question = message.question;
      state.answerLocked = false;
      if (state.room && message.endsAt) {
        state.room.endsAt = message.endsAt;
      }
      break;

    case "answer_result":
      state.result = message;
      state.answerLocked = true;
      break;

    case "scoreboard":
      if (state.room) {
        state.room.players = message.players;
      }
      break;

    case "game_over":
      state.room = message.room;
      state.durationSeconds =
        message.room.durationSeconds || state.durationSeconds;
      state.gameOver = message;
      state.roundReview = message.review || [];
      state.showReview = false;
      state.question = null;
      state.answerLocked = false;
      stopTimer();
      break;

    case "room_expired":
      state.room = null;
      state.shareUrl = "";
      state.error = message.message;
      break;

    case "questions_reloaded":
      state.bank = message.bank;
      state.error = "Question bank reloaded.";
      break;

    case "error":
      state.error = message.message;
      break;

    default:
      break;
  }

  render();
  updateTimer();
}

function syncServerTime(message) {
  if (typeof message.serverNow === "number") {
    state.serverOffsetMs = message.serverNow - Date.now();
  }
}

function serverNow() {
  return Date.now() + state.serverOffsetMs;
}

function showError(message) {
  state.error = message;
  render();
}

function clearError() {
  state.error = "";
  render();
}

function startTimer() {
  stopTimer();
  state.timerId = window.setInterval(updateTimer, 150);
}

function stopTimer() {
  if (state.timerId) {
    window.clearInterval(state.timerId);
    state.timerId = null;
  }
}

function timeLeftMs() {
  if (!state.room || !state.room.endsAt) {
    return 0;
  }
  return Math.max(0, state.room.endsAt - serverNow());
}

function currentDurationSeconds() {
  return state.room?.durationSeconds || state.durationSeconds || 60;
}

function updateTimer() {
  const timer = document.querySelector("[data-timer]");
  const meter = document.querySelector("[data-meter]");
  if (!timer || !meter) {
    return;
  }

  const left = timeLeftMs();
  timer.textContent = formatTimeLeft(left);
  const ratio = Math.max(0, Math.min(1, left / (currentDurationSeconds() * 1000)));
  meter.style.transform = `scaleX(${ratio})`;
}

function durationLabel(seconds) {
  if (seconds === 30) {
    return "30s";
  }
  const minutes = seconds / 60;
  return `${minutes} min${minutes === 1 ? "" : "s"}`;
}

function formatTimeLeft(ms) {
  const totalSeconds = Math.ceil(ms / 1000);
  if (totalSeconds < 60) {
    return `${totalSeconds}s`;
  }
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function avatarSrc(avatar = {}) {
  const bg = avatar.bg || "#2ec4b6";
  const ink = avatar.ink || "#111111";
  const accent = avatar.accent || "#ffc857";
  const shape = avatar.shape || "bolt";
  const shapeMarkup = {
    bolt: `<path d="M54 12 24 52h22l-6 36 34-46H52l2-30Z" fill="${accent}" stroke="${ink}" stroke-width="4" stroke-linejoin="round"/>`,
    rings: `<circle cx="38" cy="42" r="20" fill="${accent}" stroke="${ink}" stroke-width="4"/><circle cx="62" cy="60" r="22" fill="none" stroke="${ink}" stroke-width="6"/>`,
    grid: `<rect x="20" y="20" width="24" height="24" fill="${accent}" stroke="${ink}" stroke-width="4"/><rect x="52" y="20" width="24" height="24" fill="#fff" stroke="${ink}" stroke-width="4"/><rect x="20" y="52" width="24" height="24" fill="#fff" stroke="${ink}" stroke-width="4"/><rect x="52" y="52" width="24" height="24" fill="${accent}" stroke="${ink}" stroke-width="4"/>`,
    orbit: `<circle cx="50" cy="50" r="12" fill="${accent}" stroke="${ink}" stroke-width="4"/><ellipse cx="50" cy="50" rx="35" ry="16" fill="none" stroke="${ink}" stroke-width="5" transform="rotate(-24 50 50)"/>`,
  };
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img"><rect width="100" height="100" rx="16" fill="${bg}"/><circle cx="82" cy="18" r="10" fill="#fff" opacity=".75"/>${shapeMarkup[shape] || shapeMarkup.bolt}</svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function renderAvatar(player, className = "avatar") {
  if (!player) {
    return "";
  }
  return `<img class="${className}" alt="${escapeHtml(player.username)} avatar" src="${avatarSrc(player.avatar)}" />`;
}

function render() {
  app.innerHTML = `
    ${renderTopbar()}
    ${state.error ? renderNotice() : ""}
    <main class="shell">
      ${renderMain()}
    </main>
    <p class="footer-note">Configurable timed battles. No profiles. No match history. Invite links expire after 30 minutes.</p>
  `;
}

function renderTopbar() {
  return `
    <header class="topbar">
      <div class="brand">
        <img class="brand-mark" alt="Code Clash mark" src="${avatarSrc({
          bg: "#ffffff",
          ink: "#141414",
          accent: "#00a676",
          shape: "orbit",
        })}" />
        <div>
          <h1>Code Clash</h1>
          <p>MCQ speed rounds for core CS prep.</p>
        </div>
      </div>
      <div class="connection">
        <span class="dot ${state.connected ? "ok" : ""}"></span>
        ${state.connected ? "Live socket" : "Connecting"}
      </div>
    </header>
  `;
}

function renderNotice() {
  return `
    <div class="notice">
      <span>${escapeHtml(state.error)}</span>
      <button data-action="clear-error">Dismiss</button>
    </div>
  `;
}

function renderMain() {
  if (state.gameOver) {
    return renderGameOver();
  }
  if (state.room && state.room.status === "active") {
    return renderArena();
  }
  if (state.room && state.room.status === "waiting") {
    return renderWaitingRoom();
  }
  if (state.queued) {
    return renderQueue();
  }
  return renderLobby();
}

function renderLobby() {
  return `
    ${renderIdentity()}
    ${renderDurationPicker()}
    <section class="mode-grid" aria-label="Battle modes">
      <button class="mode-button accent-green" data-action="create-room">
        <b>Create 1v1 Link</b>
        <span>Share a private ${durationLabel(state.durationSeconds)} room. The link expires in 30 minutes.</span>
      </button>
      <button class="mode-button accent-coral" data-action="matchmaking">
        <b>Find Random Player</b>
        <span>Queue for a ${durationLabel(state.durationSeconds)} battle and start when another player arrives.</span>
      </button>
      <button class="mode-button accent-yellow" data-action="solo">
        <b>Play Solo</b>
        <span>Practice the same timed format without an opponent.</span>
      </button>
    </section>
    <section class="join-strip" aria-label="Join by room code">
      <input id="roomCodeInput" autocomplete="off" placeholder="Enter room code" maxlength="12" />
      <button class="primary-button" data-action="join-code">Join Room</button>
    </section>
  `;
}

function renderDurationPicker() {
  return `
    <section class="duration-picker" aria-label="Match duration">
      <div>
        <p class="eyebrow">Match Duration</p>
        <p class="duration-copy">Choose anything from 30 seconds to 10 minutes.</p>
      </div>
      <label class="duration-select">
        <span>Duration</span>
        <select id="durationSelect">
          ${state.durations
            .map(
              (seconds) => `
                <option value="${seconds}" ${seconds === state.durationSeconds ? "selected" : ""}>
                  ${durationLabel(seconds)}
                </option>
              `,
            )
            .join("")}
        </select>
      </label>
    </section>
  `;
}

function renderIdentity() {
  const categories = state.bank?.categories ? Object.keys(state.bank.categories) : [];
  return `
    <section class="identity">
      <div class="player-lockup">
        ${renderAvatar(state.player)}
        <div>
          <p class="eyebrow">You are</p>
          <p class="player-name">${escapeHtml(state.player?.username || "Loading player")}</p>
        </div>
      </div>
      <div class="bank-stats" aria-label="Question bank">
        <span class="pill strong">${state.bank?.total || 0} questions</span>
        ${categories.map((category) => `<span class="pill">${escapeHtml(category)}</span>`).join("")}
      </div>
    </section>
  `;
}

function renderWaitingRoom() {
  const expiresIn = state.room?.expiresAt
    ? Math.max(0, Math.ceil((state.room.expiresAt - serverNow()) / 60000))
    : 30;
  const shareUrl = state.shareUrl || `${window.location.origin}/room/${state.room.id}`;

  return `
    ${renderIdentity()}
    <section class="section">
      <h2>Waiting for opponent</h2>
      <p>Room ${escapeHtml(state.room.id)} is open for ${expiresIn} minute${expiresIn === 1 ? "" : "s"}. Match duration is ${durationLabel(state.room.durationSeconds)}.</p>
      <div class="share-box">
        <input readonly value="${escapeHtml(shareUrl)}" aria-label="Share link" />
        <button class="primary-button" data-action="copy-link">Copy Link</button>
      </div>
      ${renderScoreboard()}
      <button class="secondary-button" data-action="back-home">Leave Room</button>
    </section>
  `;
}

function renderQueue() {
  const durationSeconds = state.queuedDurationSeconds || state.durationSeconds;
  return `
    ${renderIdentity()}
    <section class="section">
      <h2>Finding a player</h2>
      <p>Queued for a ${durationLabel(durationSeconds)} battle. Keep this tab open; the match starts as soon as another player picks the same duration.</p>
      <div class="queue-pulse" aria-hidden="true"></div>
      <button class="secondary-button" data-action="leave-queue">Cancel Queue</button>
    </section>
  `;
}

function renderArena() {
  return `
    <section class="arena">
      <div class="scoreboard">
        ${renderTimer()}
        ${renderScoreboard()}
      </div>
      ${renderQuestionPanel()}
    </section>
  `;
}

function renderTimer() {
  return `
    <div class="timer-block">
      <div class="timer-line">
        <span class="pill strong">Strict ${durationLabel(currentDurationSeconds())}</span>
        <span class="timer" data-timer>${formatTimeLeft(currentDurationSeconds() * 1000)}</span>
      </div>
      <div class="meter" aria-hidden="true"><span data-meter></span></div>
    </div>
  `;
}

function renderScoreboard() {
  const players = state.room?.players || [];
  if (!players.length) {
    return `<div class="empty">Waiting for players.</div>`;
  }
  return players
    .map(
      (player) => `
        <div class="score-row">
          ${renderAvatar(player)}
          <div>
            <strong>${escapeHtml(player.username)}</strong>
            <small>${player.connected ? "Online" : "Disconnected"} | ${player.answered} answered</small>
          </div>
          <div class="score">${player.score}</div>
        </div>
      `,
    )
    .join("");
}

function renderQuestionPanel() {
  if (!state.question) {
    return `<section class="question-panel"><div class="empty">Loading next question.</div></section>`;
  }

  const labels = ["A", "B", "C", "D"];
  return `
    <section class="question-panel">
      <div class="question-meta">
        <span class="pill strong">${escapeHtml(state.question.category)}</span>
        <span class="pill">${escapeHtml(state.question.difficulty)}</span>
      </div>
      <h2 class="question-text">${escapeHtml(state.question.prompt)}</h2>
      <div class="answers">
        ${state.question.options
          .map(
            (option, index) => `
              <button class="answer-button" data-action="answer" data-index="${index}" ${state.answerLocked ? "disabled" : ""}>
                <span class="answer-key">${labels[index]}</span>
                <span>${escapeHtml(option)}</span>
              </button>
            `,
          )
          .join("")}
      </div>
      ${renderFeedback()}
    </section>
  `;
}

function renderFeedback() {
  if (!state.result) {
    return `<div class="feedback">Pick quickly. Correct answers add 1 point.</div>`;
  }
  const text = state.result.correct
    ? `Correct. Score ${state.result.score}. ${state.result.explanation || ""}`
    : `Not this one. ${state.result.explanation || ""}`;
  return `<div class="feedback ${state.result.correct ? "correct" : "wrong"}">${escapeHtml(text)}</div>`;
}

function renderGameOver() {
  const players = state.gameOver?.room?.players || [];
  const me = state.player?.id;
  const winnerId = state.gameOver?.winnerId;
  const headline = state.gameOver?.isTie
    ? "Draw"
    : winnerId
      ? winnerId === me
        ? "You won"
        : "Opponent won"
      : "Round complete";

  return `
    <section class="result-band">
      <h2 class="result-title">${headline}</h2>
      <p>Final score: ${players
        .map((player) => `${escapeHtml(player.username)} ${player.score}`)
        .join(" | ")}</p>
      <div class="scoreboard">
        ${renderScoreboard()}
      </div>
      <div class="result-actions">
        <button class="primary-button" data-action="matchmaking">Find Random Player</button>
        <button class="secondary-button" data-action="create-room">Create New Link</button>
        <button class="secondary-button" data-action="solo">Play Solo</button>
        <button class="secondary-button" data-action="toggle-review">
          ${state.showReview ? "Hide Review" : `Review Answers (${state.roundReview.length})`}
        </button>
      </div>
      ${state.showReview ? renderReviewPanel() : ""}
    </section>
  `;
}

function renderReviewPanel() {
  if (!state.roundReview.length) {
    return `<div class="empty">No answered questions in this round.</div>`;
  }

  const labels = ["A", "B", "C", "D"];
  return `
    <section class="review-panel" aria-label="Round review">
      <h3>Round Review</h3>
      ${state.roundReview
        .map((item, index) => {
          const question = item.question;
          const selected = item.selectedIndex;
          const correct = item.correctIndex;
          return `
            <article class="review-card">
              <div class="review-head">
                <span class="pill strong">Q${index + 1}</span>
                <span class="pill">${escapeHtml(question.category)}</span>
                <span class="pill">${escapeHtml(question.difficulty)}</span>
                <span class="pill ${item.correct ? "strong" : "wrong-pill"}">${item.correct ? "Correct" : "Wrong"}</span>
              </div>
              <p class="review-question">${escapeHtml(question.prompt)}</p>
              <div class="review-options">
                ${question.options
                  .map((option, optionIndex) => {
                    const classes = [
                      "review-option",
                      optionIndex === correct ? "is-correct" : "",
                      optionIndex === selected && optionIndex !== correct
                        ? "is-selected-wrong"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ");
                    const markers = [
                      optionIndex === selected ? "Your pick" : "",
                      optionIndex === correct ? "Correct" : "",
                    ]
                      .filter(Boolean)
                      .join(" | ");
                    return `
                      <div class="${classes}">
                        <b>${labels[optionIndex]}</b>
                        <span>${escapeHtml(option)}</span>
                        ${markers ? `<em>${escapeHtml(markers)}</em>` : ""}
                      </div>
                    `;
                  })
                  .join("")}
              </div>
              ${item.explanation ? `<p class="review-explanation">${escapeHtml(item.explanation)}</p>` : ""}
            </article>
          `;
        })
        .join("")}
    </section>
  `;
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) {
    return;
  }

  const action = button.dataset.action;

  if (action === "clear-error") {
    clearError();
  }

  if (action === "create-room") {
    send("create_room", { durationSeconds: state.durationSeconds });
  }

  if (action === "matchmaking") {
    send("join_matchmaking", { durationSeconds: state.durationSeconds });
  }

  if (action === "solo") {
    send("play_solo", { durationSeconds: state.durationSeconds });
  }

  if (action === "leave-queue") {
    send("leave_queue");
  }

  if (action === "back-home") {
    send("leave_room");
    state.room = null;
    state.shareUrl = "";
    window.history.pushState({}, "", "/");
    render();
  }

  if (action === "join-code") {
    const input = document.querySelector("#roomCodeInput");
    const roomId = input ? input.value : "";
    if (roomId.trim()) {
      send("join_room", { roomId });
    }
  }

  if (action === "copy-link") {
    const link = state.shareUrl || `${window.location.origin}/room/${state.room.id}`;
    try {
      await navigator.clipboard.writeText(link);
      state.error = "Link copied.";
    } catch {
      state.error = link;
    }
    render();
  }

  if (action === "answer") {
    const optionIndex = Number(button.dataset.index);
    if (!state.question || state.answerLocked || timeLeftMs() <= 0) {
      return;
    }
    state.answerLocked = true;
    render();
    send("answer", {
      questionId: state.question.id,
      optionIndex,
    });
  }

  if (action === "toggle-review") {
    state.showReview = !state.showReview;
    render();
  }
});

document.addEventListener("change", (event) => {
  if (event.target?.id !== "durationSelect") {
    return;
  }

  const nextDuration = Number(event.target.value);
  if (state.durations.includes(nextDuration)) {
    state.durationSeconds = nextDuration;
    render();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.target?.id === "roomCodeInput") {
    const roomId = event.target.value;
    if (roomId.trim()) {
      send("join_room", { roomId });
    }
  }

  const keyMap = { "1": 0, "2": 1, "3": 2, "4": 3, a: 0, b: 1, c: 2, d: 3 };
  const optionIndex = keyMap[event.key.toLowerCase()];
  if (
    optionIndex !== undefined &&
    state.question &&
    !state.answerLocked &&
    timeLeftMs() > 0
  ) {
    state.answerLocked = true;
    render();
    send("answer", {
      questionId: state.question.id,
      optionIndex,
    });
  }
});

connect();
render();
