let sqlUndoStack = [];
let sqlRedoStack = [];

const state = {
  socket: null,
  connected: false,
  player: null,
  bank: null,
  categories: [],
  selectedCategories: [],
  durations: [30, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600],
  durationSeconds: 60,
  queuedDurationSeconds: null,
  queuedCategories: [],
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
  onlineCount: 0,
  dropdownOpen: false,
  sql: {
    lessons: [],
    lesson: null,
    selectedLessonId: getSqlLessonId(),
    selectedTaskId: "",
    query: "",
    result: null,
    check: null,
    loading: false,
    error: "",
    showSolution: false,
    showHint: false,
    solved: loadSqlSolved(),
    autoCheckTimer: null,
    autoCheckSeq: 0,
    chapterStartTime: null,
    chapterStoppedMs: null,
    chapterPausedMs: null,
    questionStartTime: null,
    questionPausedMs: null,
    tasksCollapsed: false,
    tablesHidden: false,
    sqlTimerId: null,
    taskTimes: loadSqlTaskTimes(),
    savedQueries: loadSqlQueries(),
    queryEditSeq: 0,
  },
};

const app = document.querySelector("#app");

function getRouteRoomId() {
  const match = window.location.pathname.match(/^\/room\/([A-Za-z0-9]+)/);
  return match ? match[1].toUpperCase() : "";
}

function isSqlRoute() {
  return window.location.pathname === "/sql" || window.location.pathname.startsWith("/sql/");
}

function getSqlLessonId() {
  const match = window.location.pathname.match(/^\/sql\/([^/]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function loadSqlSolved() {
  try {
    return JSON.parse(window.localStorage.getItem("codeClashSqlSolved") || "{}");
  } catch {
    return {};
  }
}

function saveSqlSolved() {
  window.localStorage.setItem("codeClashSqlSolved", JSON.stringify(state.sql.solved));
}

function loadSqlTaskTimes() {
  try {
    return JSON.parse(window.localStorage.getItem("codeClashSqlTaskTimes") || "{}");
  } catch {
    return {};
  }
}

function saveSqlTaskTimes() {
  window.localStorage.setItem("codeClashSqlTaskTimes", JSON.stringify(state.sql.taskTimes));
}

function loadSqlQueries() {
  try {
    return JSON.parse(window.localStorage.getItem("codeClashSqlQueries") || "{}");
  } catch {
    return {};
  }
}

function saveSqlQueries() {
  window.localStorage.setItem("codeClashSqlQueries", JSON.stringify(state.sql.savedQueries));
}

function saveSqlQueryForTask() {
  const lessonId = state.sql.lesson?.id;
  const taskId = state.sql.selectedTaskId;
  if (!lessonId || !taskId) return;
  const query = state.sql.query.trim();
  const task = currentSqlTask();
  const starter = (task?.starter || "").trim();
  state.sql.savedQueries[lessonId] = state.sql.savedQueries[lessonId] || {};
  if (query && query !== starter) {
    state.sql.savedQueries[lessonId][taskId] = state.sql.query;
  } else {
    delete state.sql.savedQueries[lessonId]?.[taskId];
  }
  saveSqlQueries();
}

function getSavedQueryForTask(lessonId, taskId) {
  return state.sql.savedQueries[lessonId]?.[taskId] || null;
}

function saveSqlLastPosition() {
  const pos = {};
  if (state.sql.selectedLessonId) pos.lessonId = state.sql.selectedLessonId;
  if (state.sql.selectedTaskId) pos.taskId = state.sql.selectedTaskId;
  window.localStorage.setItem("codeClashSqlPosition", JSON.stringify(pos));
}

function loadSqlLastPosition() {
  try {
    return JSON.parse(window.localStorage.getItem("codeClashSqlPosition") || "{}");
  } catch {
    return {};
  }
}

function recordTaskTime(taskId) {
  const lessonId = state.sql.lesson?.id;
  if (!lessonId || !state.sql.questionStartTime) return;
  const elapsed = Math.floor((Date.now() - state.sql.questionStartTime) / 1000);
  state.sql.taskTimes[lessonId] = state.sql.taskTimes[lessonId] || {};
  if (!state.sql.taskTimes[lessonId][taskId]) {
    state.sql.taskTimes[lessonId][taskId] = elapsed;
    saveSqlTaskTimes();
  }
  if (isChapterComplete()) {
    state.sql.chapterStoppedMs = chapterElapsedMs();
    state.sql.questionStartTime = null;
  }
}

function isChapterComplete() {
  const lesson = state.sql.lesson;
  if (!lesson) return false;
  const solvedMap = state.sql.solved[lesson.id] || {};
  return lesson.tasks.every((task) => solvedMap[task.id]);
}

function getTaskTime(lessonId, taskId) {
  return state.sql.taskTimes[lessonId]?.[taskId] || null;
}

function chapterElapsedMs() {
  if (state.sql.chapterStoppedMs != null) return state.sql.chapterStoppedMs;
  if (state.sql.chapterPausedMs != null) return state.sql.chapterPausedMs;
  if (!state.sql.chapterStartTime) return 0;
  return Date.now() - state.sql.chapterStartTime;
}

function questionElapsedMs() {
  if (state.sql.questionPausedMs != null) return state.sql.questionPausedMs;
  if (!state.sql.questionStartTime) return 0;
  return Date.now() - state.sql.questionStartTime;
}

function isChapterTimerPaused() {
  return state.sql.chapterPausedMs != null;
}

function isQuestionTimerPaused() {
  return state.sql.questionPausedMs != null;
}

function pauseChapterTimer() {
  if (state.sql.chapterPausedMs != null || state.sql.chapterStoppedMs != null) return;
  state.sql.chapterPausedMs = chapterElapsedMs();
  state.sql.chapterStartTime = null;
}

function resumeChapterTimer() {
  if (state.sql.chapterPausedMs == null) return;
  state.sql.chapterStartTime = Date.now() - state.sql.chapterPausedMs;
  state.sql.chapterPausedMs = null;
}

function pauseQuestionTimer() {
  if (state.sql.questionPausedMs != null) return;
  state.sql.questionPausedMs = questionElapsedMs();
  state.sql.questionStartTime = null;
}

function resumeQuestionTimer() {
  if (state.sql.questionPausedMs == null) return;
  state.sql.questionStartTime = Date.now() - state.sql.questionPausedMs;
  state.sql.questionPausedMs = null;
}

function formatElapsed(ms) {
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function formatElapsedCompact(seconds) {
  if (seconds == null) return "";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function startSqlTimers() {
  stopSqlTimers();
  state.sql.sqlTimerId = window.setInterval(updateSqlTimers, 1000);
}

function stopSqlTimers() {
  if (state.sql.sqlTimerId) {
    window.clearInterval(state.sql.sqlTimerId);
    state.sql.sqlTimerId = null;
  }
}

function updateSqlTimers() {
  const chapterTimer = document.querySelector("[data-sql-chapter-timer]");
  if (chapterTimer) {
    chapterTimer.textContent = formatElapsed(chapterElapsedMs());
  }
  const questionTimer = document.querySelector("[data-sql-question-timer]");
  if (questionTimer) {
    questionTimer.textContent = formatElapsed(questionElapsedMs());
  }
}

function totalChapterTime(lessonId) {
  const times = state.sql.taskTimes[lessonId] || {};
  const values = Object.values(times);
  if (!values.length) return null;
  return values.reduce((a, b) => a + b, 0);
}

function resetChapterTimers() {
  const lessonId = state.sql.lesson?.id;
  if (!lessonId) return;
  delete state.sql.taskTimes[lessonId];
  saveSqlTaskTimes();
  delete state.sql.solved[lessonId];
  saveSqlSolved();
  delete state.sql.savedQueries[lessonId];
  saveSqlQueries();
  state.sql.chapterStartTime = Date.now();
  state.sql.chapterStoppedMs = null;
  state.sql.chapterPausedMs = null;
  state.sql.questionStartTime = Date.now();
  state.sql.questionPausedMs = null;
  state.sql.selectedTaskId = state.sql.lesson.tasks[0]?.id || "";
  if (state.sql.autoCheckTimer) {
    window.clearTimeout(state.sql.autoCheckTimer);
    state.sql.autoCheckTimer = null;
  }
  setSqlQueryFromTask();
  startSqlTimers();
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
    state.queuedCategories = [];
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
      state.categories =
        message.questionCategories || Object.keys(message.bank?.categories || {});
      state.selectedCategories = [...state.categories];
      state.durations = message.durations || state.durations;
      state.durationSeconds = message.defaultDurationSeconds || state.durationSeconds;
      state.onlineCount = message.onlineCount || 0;
      if (state.routeRoomId) {
        send("join_room", { roomId: state.routeRoomId });
        state.routeRoomId = "";
      }
      break;

    case "room_created":
      state.room = message.room;
      state.durationSeconds = message.room.durationSeconds || state.durationSeconds;
      state.selectedCategories = message.room.categories || selectedCategories();
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
      state.selectedCategories = message.room.categories || state.selectedCategories;
      state.queued = false;
      state.queuedDurationSeconds = null;
      state.queuedCategories = [];
      break;

    case "queued":
      state.queued = true;
      state.queuedDurationSeconds =
        message.durationSeconds || state.durationSeconds;
      state.queuedCategories = message.categories || selectedCategories();
      state.room = null;
      state.gameOver = null;
      state.roundReview = [];
      state.showReview = false;
      break;

    case "queue_left":
      state.queued = false;
      state.queuedDurationSeconds = null;
      state.queuedCategories = [];
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
      state.selectedCategories = message.room.categories || state.selectedCategories;
      state.queued = false;
      state.queuedDurationSeconds = null;
      state.queuedCategories = [];
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
      state.selectedCategories = message.room.categories || state.selectedCategories;
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

    case "global_stats":
      state.onlineCount = message.onlineCount || state.onlineCount;
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

function allCategories() {
  if (state.categories.length) {
    return state.categories;
  }
  return Object.keys(state.bank?.categories || {});
}

function selectedCategories() {
  const known = allCategories();
  const selected = state.selectedCategories.filter((category) =>
    known.includes(category),
  );
  return selected.length ? selected : known;
}

function isAllCategoriesSelected(categories = selectedCategories()) {
  const known = allCategories();
  return known.length > 0 && categories.length === known.length;
}

function categoryScopeLabel(categories = selectedCategories()) {
  if (!categories.length) {
    return "All topics";
  }
  if (isAllCategoriesSelected(categories)) {
    return "All topics";
  }
  if (categories.length <= 2) {
    return categories.join(" + ");
  }
  return `${categories.length} topics`;
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
  const editor = document.querySelector("#sqlEditor");
  const hadFocus = editor && document.activeElement === editor;
  const savedSel = hadFocus
    ? { start: editor.selectionStart, end: editor.selectionEnd }
    : null;

  const sidebar = document.querySelector(".sql-sidebar");
  const savedSidebarScroll = sidebar ? sidebar.scrollTop : null;

  app.innerHTML = `
    ${renderTopbar()}
    ${state.error ? renderNotice() : ""}
    <main class="shell">
      ${renderMain()}
    </main>
    <p class="footer-note">${isSqlRoute() ? "SQL practice runs in a fresh local sandbox for every query." : "Configurable timed battles. No profiles. No match history. Invite links expire after 30 minutes."}</p>
  `;

  if (savedSel) {
    restoreSqlEditorFocus(savedSel);
  }

  if (savedSidebarScroll !== null) {
    const newSidebar = document.querySelector(".sql-sidebar");
    if (newSidebar) newSidebar.scrollTop = savedSidebarScroll;
  }
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
          <p>${isSqlRoute() ? "Interactive SQL exercises." : "MCQ speed rounds for core CS prep."}</p>
        </div>
      </div>
      <div class="top-actions">
        <button class="nav-button ${!isSqlRoute() ? "active" : ""}" data-action="nav-battle">Battles</button>
        <div class="nav-dropdown">
          <span class="nav-dropdown-trigger ${isSqlRoute() ? "active" : ""}" data-action="nav-dropdown-toggle">Practice</span>
          <div class="nav-dropdown-menu${state.dropdownOpen ? ' open' : ''}">
            <button class="nav-dropdown-item ${isSqlRoute() ? "active" : ""}" data-action="nav-sql">SQL Practice</button>
            <a class="nav-dropdown-item" href="/lld">LLD Practice</a>
          </div>
        </div>
        <div class="connection">
          <span class="dot ${state.connected ? "ok" : ""}"></span>
          ${state.connected ? `${state.onlineCount} players live` : "Connecting"}
        </div>
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
  if (isSqlRoute()) {
    return renderSqlPractice();
  }
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
    ${renderCategoryPicker()}
    <section class="mode-grid" aria-label="Battle modes">
      <button class="mode-button accent-green" data-action="create-room">
        <b>Create 1v1 Link</b>
        <span>Share a private ${durationLabel(state.durationSeconds)} ${categoryScopeLabel()} room. The link expires in 30 minutes.</span>
      </button>
      <button class="mode-button accent-coral" data-action="matchmaking">
        <b>Find Random Player</b>
        <span>Queue for a ${durationLabel(state.durationSeconds)} ${categoryScopeLabel()} battle.</span>
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

function renderCategoryPicker() {
  const known = allCategories();
  const selected = selectedCategories();
  return `
    <section class="category-picker" aria-label="Battle type">
      <div>
        <p class="eyebrow">Battle Type</p>
        <p class="duration-copy">Pick one topic, combine topics, or keep the full mixed bank.</p>
      </div>
      <div class="category-actions">
        <button class="category-chip ${isAllCategoriesSelected(selected) ? "active" : ""}" data-action="category-all">
          All
        </button>
        ${known
          .map(
            (category) => `
              <button class="category-chip ${selected.includes(category) && !isAllCategoriesSelected(selected) ? "active" : ""}" data-action="category-toggle" data-category="${escapeHtml(category)}">
                ${escapeHtml(category)}
              </button>
            `,
          )
          .join("")}
      </div>
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
      <p>Room ${escapeHtml(state.room.id)} is open for ${expiresIn} minute${expiresIn === 1 ? "" : "s"}. Match duration is ${durationLabel(state.room.durationSeconds)} with ${categoryScopeLabel(state.room.categories || allCategories())}.</p>
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
  const categories = state.queuedCategories.length
    ? state.queuedCategories
    : selectedCategories();
  return `
    ${renderIdentity()}
    <section class="section">
      <h2>Finding a player</h2>
      <p>Queued for a ${durationLabel(durationSeconds)} ${categoryScopeLabel(categories)} battle. Keep this tab open; the match starts as soon as another player picks the same setup.</p>
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
      <div class="scoring-guide">
        <span class="pill small">+2 Correct</span>
        <span class="pill small danger">-1 Wrong</span>
        <span class="pill small">0 Skip</span>
      </div>
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
        ${(state.question.tags || [])
          .map((tag) => `<span class="pill company-tag">${escapeHtml(tag)}</span>`)
          .join("")}
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
      <div class="question-actions">
        <button class="secondary-button skip-button" data-action="skip" data-id="${state.question.id}">Skip Question</button>
      </div>
      ${renderFeedback()}
    </section>
  `;
}

function renderFeedback() {
  if (!state.result) {
    return `<div class="feedback">Pick quickly. Correct: +2 pts | Wrong: -1 pt</div>`;
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

async function loadSqlIndex() {
  if (state.sql.loading || state.sql.lessons.length) {
    return;
  }
  state.sql.loading = true;
  state.sql.error = "";
  render();
  try {
    const response = await fetch("/api/sql/lessons");
    const payload = await response.json();
    state.sql.lessons = payload.lessons || [];
    const lastPos = loadSqlLastPosition();
    const lessonId = state.sql.selectedLessonId || lastPos.lessonId || state.sql.lessons[0]?.id || "";
    if (lastPos.taskId && lessonId === lastPos.lessonId) {
      state.sql.selectedTaskId = lastPos.taskId;
    }
    if (lessonId) {
      await loadSqlLesson(lessonId, false);
    }
  } catch (error) {
    state.sql.error = error.message || "Could not load SQL lessons.";
  } finally {
    state.sql.loading = false;
    render();
  }
}

async function loadSqlLesson(lessonId, pushRoute = true) {
  if (!lessonId) {
    return;
  }
  state.sql.loading = true;
  state.sql.error = "";
  state.sql.result = null;
  state.sql.check = null;
  state.sql.showSolution = false;
  render();
  try {
    const response = await fetch(`/api/sql/lessons/${encodeURIComponent(lessonId)}`);
    const payload = await response.json();
    state.sql.lesson = payload.lesson;
    state.sql.selectedLessonId = payload.lesson.id;
    const route = `/sql/${payload.lesson.id}`;
    if (pushRoute && window.location.pathname !== route) {
      window.history.pushState({}, "", route);
    }

    const lastPos = loadSqlLastPosition();
    const currentTask = payload.lesson.tasks.find(
      (task) => task.id === state.sql.selectedTaskId,
    );
    const resumeTaskId = currentTask?.id
      || (lastPos.lessonId === payload.lesson.id ? lastPos.taskId : "")
      || payload.lesson.tasks[0]?.id
      || "";
    state.sql.selectedTaskId = resumeTaskId;
    state.sql.chapterStartTime = Date.now();
    state.sql.chapterStoppedMs = null;
    state.sql.questionStartTime = Date.now();
    startSqlTimers();
    saveSqlLastPosition();
    setSqlQueryFromTask();
  } catch (error) {
    state.sql.error = error.message || "Could not load this chapter.";
  } finally {
    state.sql.loading = false;
    render();
  }
}

function setSqlQueryFromTask() {
  if (state.sql.autoCheckTimer) {
    window.clearTimeout(state.sql.autoCheckTimer);
    state.sql.autoCheckTimer = null;
  }
  // Invalidate any in-flight auto-check from the previous task so its
  // response doesn't trigger an advance after we've switched away.
  ++state.sql.autoCheckSeq;
  const task = currentSqlTask();
  const lessonId = state.sql.lesson?.id;
  const taskId = state.sql.selectedTaskId;
  const saved = lessonId && taskId ? getSavedQueryForTask(lessonId, taskId) : null;
  const alreadySolved = lessonId && taskId && isSqlTaskSolved(taskId);
  state.sql.query = saved != null ? saved : (task?.starter || "");
  state.sql.result = null;
  state.sql.check = null;
  state.sql.showSolution = false;
  state.sql.showHint = false;
  state.sql.questionStartTime = Date.now();
  state.sql.questionPausedMs = null;
  saveSqlLastPosition();
  // Auto-run if the user has a saved in-progress query or the task is already solved,
  // so the result grid populates immediately (SQLBolt-style UX).
  // But do NOT auto-advance if the user is revisiting an already-solved task.
  if (state.sql.query.trim() && (saved != null || alreadySolved)) {
    if (alreadySolved) {
      // Just run the query to show results — don't advance away
      runSqlAction(false, { auto: true, preserveEditor: true });
    } else {
      scheduleSqlAutoCheck();
    }
  }
}

function currentSqlTask() {
  return state.sql.lesson?.tasks.find((task) => task.id === state.sql.selectedTaskId);
}

function isSqlTaskSolved(taskId) {
  const lessonId = state.sql.lesson?.id;
  return Boolean(lessonId && state.sql.solved[lessonId]?.[taskId]);
}

function markSqlTaskSolved(taskId) {
  const lessonId = state.sql.lesson?.id;
  if (!lessonId) {
    return;
  }
  state.sql.solved[lessonId] = state.sql.solved[lessonId] || {};
  state.sql.solved[lessonId][taskId] = true;
  saveSqlSolved();
}

function nextSqlTaskId() {
  const tasks = state.sql.lesson?.tasks || [];
  const currentIndex = tasks.findIndex((task) => task.id === state.sql.selectedTaskId);
  if (currentIndex === -1) {
    return "";
  }
  const laterUnsolved = tasks
    .slice(currentIndex + 1)
    .find((task) => !isSqlTaskSolved(task.id));
  return laterUnsolved?.id || tasks[currentIndex + 1]?.id || "";
}

function advanceSqlTask() {
  const nextTaskId = nextSqlTaskId();
  if (!nextTaskId) {
    return false;
  }
  state.sql.selectedTaskId = nextTaskId;
  setSqlQueryFromTask();
  return true;
}

function restoreSqlEditorFocus(selection) {
  if (!selection) {
    return;
  }
  const editor = document.querySelector("#sqlEditor");
  if (!editor) {
    return;
  }
  editor.focus();
  const start = Math.min(selection.start, editor.value.length);
  const end = Math.min(selection.end, editor.value.length);
  if (editor.selectionStart !== start || editor.selectionEnd !== end) {
    editor.setSelectionRange(start, end);
  }
}

function sqlEditorSelection() {
  const editor = document.querySelector("#sqlEditor");
  if (!editor || document.activeElement !== editor) {
    return null;
  }
  return {
    start: editor.selectionStart,
    end: editor.selectionEnd,
  };
}

function scheduleSqlAutoCheck() {
  if (state.sql.autoCheckTimer) {
    window.clearTimeout(state.sql.autoCheckTimer);
  }
  const sql = state.sql.query.trim();
  if (!sql || !state.sql.lesson || !currentSqlTask()) {
    return;
  }
  const seq = ++state.sql.autoCheckSeq;
  state.sql.autoCheckTimer = window.setTimeout(() => {
    runSqlAction(true, {
      auto: true,
      advanceOnCorrect: true,
      preserveEditor: true,
      seq,
    });
  }, 850);
}

function solvedCountForLesson(lessonId) {
  const lesson = state.sql.lessons.find((item) => item.id === lessonId);
  const solved = state.sql.solved[lessonId] || {};
  return lesson ? Object.keys(solved).filter((taskId) => solved[taskId]).length : 0;
}

function renderSqlPractice() {
  if (!state.sql.lessons.length && !state.sql.loading && !state.sql.error) {
    window.setTimeout(loadSqlIndex, 0);
  }

  return `
    <section class="sql-shell">
      ${renderSqlSidebar()}
      ${renderSqlWorkspace()}
    </section>
  `;
}

function renderSqlSidebar() {
  return `
    <aside class="sql-sidebar" aria-label="SQL chapters">
      <div class="sql-sidebar-head">
        <p class="eyebrow">SQL Practice</p>
        <h2>Chapters</h2>
      </div>
        <div class="sql-chapter-list">
          ${(() => {
            const groups = {};
            for (const lesson of state.sql.lessons) {
              const g = lesson.group || "Other";
              if (!groups[g]) groups[g] = [];
              groups[g].push(lesson);
            }
            return Object.entries(groups).map(([group, lessons]) => `
              <div class="sql-chapter-group">
                <div class="sql-chapter-group-title">${escapeHtml(group)}</div>
                ${lessons.map(lesson => {
                  const solved = solvedCountForLesson(lesson.id);
                  const totalTime = totalChapterTime(lesson.id);
                  return `
                    <button class="sql-chapter ${state.sql.lesson?.id === lesson.id ? "active" : ""}" data-action="sql-lesson" data-lesson-id="${escapeHtml(lesson.id)}">
                      <span>${lesson.number}</span>
                      <b>${escapeHtml(lesson.title)}</b>
                      <small>${solved}/${lesson.taskCount}${totalTime != null ? ` · ${formatElapsedCompact(totalTime)}` : ""}</small>
                    </button>
                  `;
                }).join("")}
              </div>
            `).join("");
          })()}
        </div>
    </aside>
  `;
}

function renderSqlWorkspace() {
  if (state.sql.error) {
    return `<section class="sql-workspace"><div class="empty">${escapeHtml(state.sql.error)}</div></section>`;
  }
  if (state.sql.loading && !state.sql.lesson) {
    return `<section class="sql-workspace"><div class="empty">Loading SQL practice.</div></section>`;
  }
  if (!state.sql.lesson) {
    return `<section class="sql-workspace"><div class="empty">Choose a SQL chapter.</div></section>`;
  }

  return `
    <section class="sql-workspace">
      <div class="sql-lesson-head">
        <div>
          <p class="eyebrow">Chapter ${state.sql.lesson.number}</p>
          <h2>${escapeHtml(state.sql.lesson.title)}</h2>
        </div>
        <div class="lesson-tools">
          <div class="sql-chapter-timer-block${(state.sql.chapterStoppedMs != null || state.sql.chapterPausedMs != null) ? ' stopped' : ''}">
            <span class="sql-timer-icon">⏱</span>
            <span class="sql-timer-value" data-sql-chapter-timer>${formatElapsed(chapterElapsedMs())}</span>
            ${state.sql.chapterStoppedMs == null && (state.sql.chapterStartTime || state.sql.chapterPausedMs != null) ? `
              <button class="sql-timer-reset" data-action="sql-pause-chapter" title="${isChapterTimerPaused() ? 'Resume chapter timer' : 'Pause chapter timer'}" aria-label="${isChapterTimerPaused() ? 'Resume' : 'Pause'} chapter timer">${isChapterTimerPaused() ? '▶' : '⏸'}</button>
            ` : ''}
            ${state.sql.chapterStartTime || state.sql.chapterStoppedMs != null || state.sql.chapterPausedMs != null ? `<button class="sql-timer-reset" data-action="sql-reset-timers" title="Reset chapter &amp; question timers">↻</button>` : ""}
          </div>
          <div class="question-meta">
            ${state.sql.lesson.focus.map((focus) => `<span class="pill">${escapeHtml(focus)}</span>`).join("")}
          </div>
          <button class="secondary-button compact" data-action="sql-toggle-tables">${state.sql.tablesHidden ? '⊞ Show Tables' : '⊟ Hide Tables'}</button>
          ${state.sql.lesson.notesUrl ? `<a class="notes-link" href="${escapeHtml(state.sql.lesson.notesUrl)}" target="_blank" rel="noreferrer">Notes</a>` : ""}
        </div>
      </div>
      <div class="sql-grid">
        ${!state.sql.tablesHidden ? `
        <div class="sql-left">
          ${renderSqlTables()}
        </div>
        ` : ''}
        <div class="sql-right">
          ${renderSqlTasks()}
          ${renderSqlEditor()}
          ${renderSqlFeedback()}
          ${renderSqlResult()}
        </div>
      </div>
    </section>
  `;
}

function renderSqlTables() {
  const task = currentSqlTask();
  const tables = task?.tables?.length ? task.tables : state.sql.lesson.tables;
  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>Tables</h3>
        <button class="secondary-button compact" data-action="sql-reset">Reset Query</button>
      </div>
      <div class="sql-table-stack">
        ${tables.map((table) => renderSqlTable(table)).join("")}
      </div>
    </section>
  `;
}

function renderSqlTable(table) {
  return `
    <article class="data-table-card">
      <div class="data-table-title">
        <b>${escapeHtml(table.name)}</b>
        <span>${table.total} rows</span>
      </div>
      <div class="data-table-wrap">
        <table>
          <thead>
            <tr>${table.columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr>
          </thead>
          <tbody>
            ${table.rows
              .map(
                (row) => `
                  <tr>${row.map((value) => `<td>${escapeHtml(value ?? "NULL")}</td>`).join("")}</tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </article>
  `;
}

function renderSqlTasks() {
  const collapsed = state.sql.tasksCollapsed;
  const tasks = collapsed
    ? state.sql.lesson.tasks.filter((t) => t.id === state.sql.selectedTaskId)
    : state.sql.lesson.tasks;
  return `
    <section class="sql-panel task-panel">
      <div class="sql-panel-head">
        <h3>Exercises</h3>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="pill strong">${solvedCountForLesson(state.sql.lesson.id)}/${state.sql.lesson.tasks.length} solved</span>
          <button class="secondary-button compact" data-action="sql-toggle-tasks" title="${collapsed ? 'Show all exercises' : 'Focus on current exercise'}">${collapsed ? 'All' : 'Focus'}</button>
        </div>
      </div>
      <div class="sql-task-list">
        ${tasks
          .map(
            (task) => {
              const index = state.sql.lesson.tasks.indexOf(task);
              const solveTime = getTaskTime(state.sql.lesson.id, task.id);
              return `
              <button class="sql-task ${task.id === state.sql.selectedTaskId ? "active" : ""} ${isSqlTaskSolved(task.id) ? "solved" : ""}" data-action="sql-task" data-task-id="${escapeHtml(task.id)}">
                <span>${isSqlTaskSolved(task.id) ? "✓" : index + 1}</span>
                <b>${escapeHtml(task.prompt)}</b>
                ${solveTime != null ? `<small class="task-time">${formatElapsedCompact(solveTime)}</small>` : ""}
              </button>
            `;
            },
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderSqlEditor() {
  const task = currentSqlTask();
  return `
    <section class="sql-panel editor-panel">
      <div class="sql-panel-head">
        <h3>${escapeHtml(task?.prompt || "SQL")}</h3>
        <div class="editor-actions">
          <div class="sql-question-timer-block${state.sql.questionPausedMs != null ? ' stopped' : ''}">
            <span class="sql-timer-icon">⏱</span>
            <span class="sql-timer-value" data-sql-question-timer>${formatElapsed(questionElapsedMs())}</span>
            <button class="sql-timer-reset" data-action="sql-pause-question" title="${isQuestionTimerPaused() ? 'Resume question timer' : 'Pause question timer'}" aria-label="${isQuestionTimerPaused() ? 'Resume' : 'Pause'} question timer">${isQuestionTimerPaused() ? '▶' : '⏸'}</button>
            <button class="sql-timer-reset" data-action="sql-reset-question-timer" title="Reset question timer" aria-label="Reset question timer">↻</button>
          </div>
          <button class="secondary-button compact" data-action="sql-hint">${state.sql.showHint ? "Hide Hint" : "💡 Hint"}</button>
          <button class="secondary-button compact" data-action="sql-solution">${state.sql.showSolution ? "Hide Solution" : "Solution"}</button>
          <button class="secondary-button compact" data-action="sql-run">Run</button>
          <button class="primary-button compact" data-action="sql-check">Check</button>
        </div>
      </div>
      <textarea id="sqlEditor" spellcheck="false">${escapeHtml(state.sql.query)}</textarea>
      ${state.sql.showHint && task?.hint ? `<p class="sql-hint">💡 ${escapeHtml(task.hint)}</p>` : ""}
    </section>
  `;
}

function renderSqlFeedback() {
  if (!state.sql.check && !state.sql.showSolution) {
    return "";
  }
  const task = currentSqlTask();
  const check = state.sql.check;
  return `
    <section class="feedback ${check?.correct ? "correct" : check ? "wrong" : ""}">
      ${check ? escapeHtml(check.message) : ""}
      ${state.sql.showSolution && check?.solution ? `<pre>${escapeHtml(check.solution)}</pre>` : ""}
      ${state.sql.showSolution && !check?.solution && task ? `<pre>Run Check to reveal the solution for this task.</pre>` : ""}
    </section>
  `;
}

function renderSqlResult() {
  const result = state.sql.result || state.sql.check?.result;
  if (!result) {
    return `<section class="sql-panel"><div class="empty compact-empty">Run a query to see the result grid.</div></section>`;
  }

  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>Result</h3>
        <span class="pill">${result.rowCount || 0} rows</span>
      </div>
      ${result.message ? `<p class="sql-message">${escapeHtml(result.message)}</p>` : ""}
      ${renderResultGrid(result)}
      ${state.sql.check?.expected ? `
        <div class="expected-block">
          <h3>Expected</h3>
          ${renderResultGrid(state.sql.check.expected)}
        </div>
      ` : ""}
    </section>
  `;
}

function renderResultGrid(result) {
  if (!result.columns?.length) {
    return "";
  }
  return `
    <div class="data-table-wrap result-grid">
      <table>
        <thead>
          <tr>${result.columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${result.rows
            .map(
              (row) => `
                <tr>${row.map((value) => `<td>${escapeHtml(value ?? "NULL")}</td>`).join("")}</tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function runSqlAction(check = false, options = {}) {
  if (!state.sql.lesson || !currentSqlTask()) {
    return;
  }
  let advanced = false;
  const selection = options.preserveEditor ? sqlEditorSelection() : null;
  const editSeqAtStart = state.sql.queryEditSeq;
  state.sql.loading = !options.auto;
  state.sql.error = "";
  if (!options.auto) {
    state.sql.check = null;
  }
  if (!check) {
    state.sql.result = null;
  }
  if (!options.auto) {
    render();
  }

  const url = check ? "/api/sql/check" : "/api/sql/run";
  const payload = {
    lessonId: state.sql.lesson.id,
    sql: state.sql.query,
  };
  if (check) {
    payload.taskId = state.sql.selectedTaskId;
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!data.ok) {
      throw new Error(data.error || "SQL failed.");
    }
    if (options.seq && options.seq !== state.sql.autoCheckSeq) {
      return;
    }
    if (check) {
      state.sql.check = data;
      state.sql.result = data.result;
      if (data.correct) {
        markSqlTaskSolved(state.sql.selectedTaskId);
        recordTaskTime(state.sql.selectedTaskId);
        if (options.advanceOnCorrect) {
          advanced = advanceSqlTask();
        }
      } else if (options.auto) {
        state.sql.check = null;
      }
    } else {
      state.sql.result = data.result;
    }
  } catch (error) {
    if (options.seq && options.seq !== state.sql.autoCheckSeq) {
      return;
    }
    state.sql.check = {
      correct: false,
      message: error.message || "SQL failed.",
    };
  } finally {
    state.sql.loading = false;
    render();
    if (
      options.preserveEditor &&
      !advanced &&
      !state.sql.check?.correct &&
      state.sql.queryEditSeq === editSeqAtStart
    ) {
      restoreSqlEditorFocus(selection);
    }
  }
}

document.addEventListener("click", async (event) => {
  // Close dropdown if click is outside the nav-dropdown
  if (!event.target.closest(".nav-dropdown")) {
    if (state.dropdownOpen) {
      state.dropdownOpen = false;
      render();
    }
  }

  const button = event.target.closest("[data-action]");
  if (!button) {
    return;
  }

  const action = button.dataset.action;

  if (action === "nav-dropdown-toggle") {
    state.dropdownOpen = !state.dropdownOpen;
    render();
    return;
  }

  // Close dropdown on any other action
  state.dropdownOpen = false;

  if (action === "clear-error") {
    clearError();
  }

  if (action === "nav-sql") {
    window.history.pushState({}, "", state.sql.selectedLessonId ? `/sql/${state.sql.selectedLessonId}` : "/sql");
    loadSqlIndex();
    render();
  }

  if (action === "nav-battle") {
    window.history.pushState({}, "", "/");
    render();
  }

  if (action === "sql-lesson") {
    await loadSqlLesson(button.dataset.lessonId);
  }

  if (action === "sql-task") {
    saveSqlQueryForTask();
    state.sql.selectedTaskId = button.dataset.taskId;
    setSqlQueryFromTask();
    render();
  }

  if (action === "sql-reset") {
    setSqlQueryFromTask();
    render();
  }

  if (action === "sql-toggle-tasks") {
    state.sql.tasksCollapsed = !state.sql.tasksCollapsed;
    render();
  }

  if (action === "sql-toggle-tables") {
    state.sql.tablesHidden = !state.sql.tablesHidden;
    render();
  }

  if (action === "sql-reset-timers") {
    resetChapterTimers();
    render();
  }

  if (action === "sql-pause-chapter") {
    if (isChapterTimerPaused()) {
      resumeChapterTimer();
    } else {
      pauseChapterTimer();
    }
    render();
  }

  if (action === "sql-pause-question") {
    if (isQuestionTimerPaused()) {
      resumeQuestionTimer();
    } else {
      pauseQuestionTimer();
    }
    render();
  }

  if (action === "sql-reset-question-timer") {
    state.sql.questionPausedMs = null;
    state.sql.questionStartTime = Date.now();
    render();
  }

  if (action === "sql-run") {
    await runSqlAction(false);
  }

  if (action === "sql-check") {
    await runSqlAction(true, { advanceOnCorrect: true });
  }

  if (action === "sql-hint") {
    state.sql.showHint = !state.sql.showHint;
    render();
  }

  if (action === "sql-solution") {
    state.sql.showSolution = !state.sql.showSolution;
    if (state.sql.showSolution && !state.sql.check?.solution) {
      await runSqlAction(true, { advanceOnCorrect: false });
      state.sql.showSolution = true;
    }
    render();
  }

  if (action === "create-room") {
    send("create_room", {
      durationSeconds: state.durationSeconds,
      categories: selectedCategories(),
    });
  }

  if (action === "matchmaking") {
    send("join_matchmaking", {
      durationSeconds: state.durationSeconds,
      categories: selectedCategories(),
    });
  }

  if (action === "solo") {
    send("play_solo", {
      durationSeconds: state.durationSeconds,
      categories: selectedCategories(),
    });
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

  if (action === "skip") {
    if (!state.question || state.answerLocked || timeLeftMs() <= 0) {
      return;
    }
    send("skip", {
      questionId: state.question.id,
    });
  }

  if (action === "toggle-review") {
    state.showReview = !state.showReview;
    render();
  }

  if (action === "category-all") {
    state.selectedCategories = [...allCategories()];
    render();
  }

  if (action === "category-toggle") {
    const category = button.dataset.category;
    const known = allCategories();
    if (!known.includes(category)) {
      return;
    }

    const current = selectedCategories();
    const currentSet = new Set(
      isAllCategoriesSelected(current) ? [] : current,
    );

    if (currentSet.has(category)) {
      currentSet.delete(category);
    } else {
      currentSet.add(category);
    }

    state.selectedCategories = currentSet.size
      ? known.filter((knownCategory) => currentSet.has(knownCategory))
      : [category];
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

document.addEventListener("input", (event) => {
  if (event.target?.id === "sqlEditor") {
    // Only save to undo stack on spaces, newlines, or deletions to chunk history reasonably
    if (event.data === " " || event.data === null || event.inputType === "insertLineBreak" || sqlUndoStack.length === 0) {
      if (sqlUndoStack[sqlUndoStack.length - 1] !== state.sql.query) {
        sqlUndoStack.push(state.sql.query);
        sqlRedoStack = [];
      }
    }

    state.sql.query = event.target.value;
    saveSqlQueryForTask();
    scheduleSqlAutoCheck();
    // Only do a full render if we need to clear a visible check result;
    // otherwise skip render entirely to avoid destroying/recreating the
    // textarea which causes the cursor to jump left randomly.
    if (state.sql.check) {
      state.sql.check = null;
      // Targeted clear: remove only the feedback badge instead of full render
      const badge = document.querySelector(".sql-check-badge");
      if (badge) badge.remove();
      const feedback = document.querySelector(".feedback");
      if (feedback) feedback.innerHTML = '<div class="empty compact-empty">Run your query or press Check.</div>';
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.target?.id === "sqlEditor") {
    if ((event.metaKey || event.ctrlKey) && (event.key.toLowerCase() === "z" || event.key.toLowerCase() === "y")) {
      event.preventDefault();
      if ((event.key.toLowerCase() === "z" && event.shiftKey) || event.key.toLowerCase() === "y") {
        // Redo
        if (sqlRedoStack.length > 0) {
          sqlUndoStack.push(state.sql.query);
          state.sql.query = sqlRedoStack.pop();
          saveSqlQueryForTask();
          render();
        }
      } else {
        // Undo
        if (sqlUndoStack.length > 0) {
          sqlRedoStack.push(state.sql.query);
          state.sql.query = sqlUndoStack.pop();
          saveSqlQueryForTask();
          render();
        }
      }
      return;
    }

    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      runSqlAction(event.shiftKey);
    }
    return;
  }

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

  if (
    event.key.toLowerCase() === "s" &&
    state.question &&
    !state.answerLocked &&
    timeLeftMs() > 0
  ) {
    send("skip", {
      questionId: state.question.id,
    });
  }
});

window.addEventListener("popstate", () => {
  state.routeRoomId = getRouteRoomId();
  state.sql.selectedLessonId = getSqlLessonId();
  if (isSqlRoute()) {
    if (state.sql.selectedLessonId && state.sql.selectedLessonId !== state.sql.lesson?.id) {
      loadSqlLesson(state.sql.selectedLessonId, false);
    } else {
      loadSqlIndex();
    }
  }
  render();
});

connect();
if (isSqlRoute()) {
  loadSqlIndex();
}
render();
