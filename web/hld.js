const state = {
  lessons: [],
  lesson: null,
  selectedLessonId: getHldLessonId(),
  selectedTaskId: "",
  loading: false,
  dropdownOpen: false,
  error: "",
  check: null,
  selectedAnswer: null,
  solved: loadJson("codeClashHldSolved"),
  quizAnswers: loadJson("codeClashHldQuizAnswers"),
  taskTimes: loadJson("codeClashHldTaskTimes"),
  chapterStartTime: null,
  chapterStoppedMs: null,
  questionStartTime: null,
  timerId: null,
};

const app = document.querySelector("#hld-app");

function getHldLessonId() {
  const match = window.location.pathname.match(/^\/hld\/([^/]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function loadJson(key) {
  try {
    return JSON.parse(window.localStorage.getItem(key) || "{}");
  } catch {
    return {};
  }
}

function saveJson(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}

function saveSolved() {
  saveJson("codeClashHldSolved", state.solved);
}

function saveQuizAnswers() {
  saveJson("codeClashHldQuizAnswers", state.quizAnswers);
}

function saveTaskTimes() {
  saveJson("codeClashHldTaskTimes", state.taskTimes);
}

function saveLastPosition() {
  saveJson("codeClashHldPosition", {
    lessonId: state.selectedLessonId,
    taskId: state.selectedTaskId,
  });
}

function loadLastPosition() {
  return loadJson("codeClashHldPosition");
}

function currentTask() {
  return state.lesson?.tasks.find((task) => task.id === state.selectedTaskId) || null;
}

function currentAnswer(lessonId, taskId) {
  return state.quizAnswers[lessonId]?.[taskId] ?? null;
}

function solvedCountForLesson(lessonId) {
  return Object.keys(state.solved[lessonId] || {}).length;
}

function totalLessonTime(lessonId) {
  const times = state.taskTimes[lessonId];
  if (!times || !Object.keys(times).length) {
    return null;
  }
  return Object.values(times).reduce((acc, current) => acc + current, 0);
}

function chapterElapsedMs() {
  if (state.chapterStoppedMs != null) {
    return state.chapterStoppedMs;
  }
  if (!state.chapterStartTime) {
    return 0;
  }
  return Date.now() - state.chapterStartTime;
}

function startChapterTimer() {
  state.chapterStartTime = Date.now();
  state.chapterStoppedMs = null;
  if (state.timerId) {
    clearInterval(state.timerId);
  }
  state.timerId = setInterval(() => {
    const timerEl = document.querySelector("[data-hld-chapter-timer]");
    if (timerEl) {
      timerEl.textContent = formatElapsed(chapterElapsedMs());
    }
  }, 1000);
}

function stopChapterTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
  state.chapterStoppedMs = chapterElapsedMs();
}

function resetChapterTimer() {
  state.chapterStartTime = Date.now();
  state.chapterStoppedMs = null;
  if (!state.timerId) {
    state.timerId = setInterval(() => {
      const timerEl = document.querySelector("[data-hld-chapter-timer]");
      if (timerEl) {
        timerEl.textContent = formatElapsed(chapterElapsedMs());
      }
    }, 1000);
  }
}

function startQuestionTimer() {
  state.questionStartTime = Date.now();
}

function recordQuestionTime() {
  if (!state.questionStartTime || !state.lesson || !state.selectedTaskId) {
    return;
  }
  const elapsed = Date.now() - state.questionStartTime;
  const lessonId = state.lesson.id;
  const taskId = state.selectedTaskId;
  state.taskTimes[lessonId] = state.taskTimes[lessonId] || {};
  state.taskTimes[lessonId][taskId] = (state.taskTimes[lessonId][taskId] || 0) + elapsed;
  saveTaskTimes();
  state.questionStartTime = null;
}

function formatElapsed(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  const displaySec = String(seconds % 60).padStart(2, "0");
  const displayMin = String(minutes % 60).padStart(2, "0");
  if (hours > 0) {
    return `${hours}:${displayMin}:${displaySec}`;
  }
  return `${displayMin}:${displaySec}`;
}

function formatElapsedCompact(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  if (minutes > 0) {
    return `${minutes}m`;
  }
  return `${seconds}s`;
}

async function loadIndex() {
  if (state.loading || state.lessons.length) {
    return;
  }
  state.loading = true;
  state.error = "";
  render();
  try {
    const response = await fetch("/api/hld/lessons");
    const payload = await response.json();
    state.lessons = payload.lessons || [];
    const last = loadLastPosition();
    const lessonId = state.selectedLessonId || last.lessonId || state.lessons[0]?.id || "";
    if (lessonId) {
      await loadLesson(lessonId, false);
    }
  } catch (error) {
    state.error = error.message || "Could not load HLD lessons.";
  } finally {
    state.loading = false;
    render();
  }
}

async function loadLesson(lessonId, pushRoute = true) {
  if (!lessonId) {
    return;
  }
  state.loading = true;
  state.error = "";
  state.check = null;
  state.selectedAnswer = null;
  render();
  try {
    const response = await fetch(`/api/hld/lessons/${encodeURIComponent(lessonId)}`);
    const payload = await response.json();
    state.lesson = payload.lesson;
    state.selectedLessonId = payload.lesson.id;
    const route = `/hld/${payload.lesson.id}`;
    if (pushRoute && window.location.pathname !== route) {
      window.history.pushState({}, "", route);
    }

    const last = loadLastPosition();
    const current = payload.lesson.tasks.find((task) => task.id === state.selectedTaskId);
    state.selectedTaskId =
      current?.id ||
      (last.lessonId === payload.lesson.id ? last.taskId : "") ||
      payload.lesson.tasks[0]?.id ||
      "";

    const allSolved = payload.lesson.tasks.every(
      (task) => state.solved[payload.lesson.id]?.[task.id]
    );

    if (allSolved) {
      stopChapterTimer();
    } else {
      startChapterTimer();
    }

    startQuestionTimer();
    saveLastPosition();
  } catch (error) {
    state.error = error.message || "Could not load lesson.";
  } finally {
    state.loading = false;
    render();
  }
}

async function checkTask() {
  const task = currentTask();
  const lessonId = state.lesson?.id;
  if (!task || !lessonId || state.loading) {
    return;
  }

  if (state.selectedAnswer == null) {
    state.error = "Please select an answer first.";
    render();
    return;
  }

  state.loading = true;
  state.error = "";
  render();
  try {
    const response = await fetch("/api/hld/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lessonId: lessonId,
        taskId: task.id,
        answer: state.selectedAnswer,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Failed to check solution.");
    }

    state.check = {
      correct: payload.correct,
      message: payload.message,
      explanation: payload.explanation,
      expectedIndex: payload.expectedIndex,
      solution: payload.solution,
    };

    recordQuestionTime();

    if (payload.correct) {
      state.solved[lessonId] = state.solved[lessonId] || {};
      state.solved[lessonId][task.id] = true;
      saveSolved();

      state.quizAnswers[lessonId] = state.quizAnswers[lessonId] || {};
      state.quizAnswers[lessonId][task.id] = state.selectedAnswer;
      saveQuizAnswers();
    }

    const allSolved = state.lesson.tasks.every(
      (t) => state.solved[lessonId]?.[t.id]
    );
    if (allSolved) {
      stopChapterTimer();
    }
  } catch (error) {
    state.error = error.message || "An error occurred checking solution.";
  } finally {
    state.loading = false;
    render();
  }
}

function handleAction(event) {
  const target = event.target.closest("[data-action]");
  if (!target) {
    return;
  }

  event.preventDefault();
  const action = target.getAttribute("data-action");

  if (action === "nav-dropdown-toggle") {
    state.dropdownOpen = !state.dropdownOpen;
    render();
    return;
  }

  if (action === "toggle-theme") {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    render();
    return;
  }

  state.dropdownOpen = false;

  if (action === "hld-lesson") {
    const lessonId = target.getAttribute("data-lesson-id");
    loadLesson(lessonId);
  } else if (action === "hld-task") {
    recordQuestionTime();
    state.selectedTaskId = target.getAttribute("data-task-id");
    state.check = null;
    const previousAnswer = currentAnswer(state.lesson?.id, state.selectedTaskId);
    state.selectedAnswer = previousAnswer;
    startQuestionTimer();
    saveLastPosition();
    render();
  } else if (action === "hld-select-option") {
    if (state.check?.correct) {
      return;
    }
    state.selectedAnswer = parseInt(target.getAttribute("data-option-index"), 10);
    render();
  } else if (action === "hld-check") {
    checkTask();
  } else if (action === "hld-next") {
    recordQuestionTime();
    const currentIdx = state.lesson.tasks.findIndex((t) => t.id === state.selectedTaskId);
    if (currentIdx !== -1 && currentIdx < state.lesson.tasks.length - 1) {
      state.selectedTaskId = state.lesson.tasks[currentIdx + 1].id;
      state.check = null;
      const previousAnswer = currentAnswer(state.lesson?.id, state.selectedTaskId);
      state.selectedAnswer = previousAnswer;
      startQuestionTimer();
      saveLastPosition();
    }
    render();
  } else if (action === "hld-reset-lesson") {
    if (confirm("Reset progress for this chapter?")) {
      const lessonId = state.lesson?.id;
      if (lessonId) {
        delete state.solved[lessonId];
        delete state.quizAnswers[lessonId];
        delete state.taskTimes[lessonId];
        saveSolved();
        saveQuizAnswers();
        saveTaskTimes();
        resetChapterTimer();
        state.check = null;
        state.selectedAnswer = null;
        if (state.lesson.tasks.length) {
          state.selectedTaskId = state.lesson.tasks[0].id;
        }
        startQuestionTimer();
        render();
      }
    }
  } else if (action === "clear-error") {
    state.error = "";
    render();
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function render() {
  app.innerHTML = `
    ${renderTopbar()}
    <main class="workspace-wrapper">
      ${state.error ? renderError() : ""}
      ${renderPractice()}
    </main>
  `;
}

function renderTopbar() {
  const isDark = (document.documentElement.getAttribute('data-theme') || 'light') === 'dark';
  return `
    <header class="topbar hld-topbar">
      <div class="brand" style="cursor: pointer;" onclick="window.location.href='/'">
        <div class="hld-brand-mark">HLD</div>
        <div>
          <h1>Code Clash</h1>
          <p>System design architectural practice, interactive quizzes, and case studies.</p>
        </div>
      </div>
      <div class="nav-links" style="display: flex; align-items: center; gap: 10px;">
        <button class="nav-button" data-action="toggle-theme" title="Toggle dark mode" style="padding: 0 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.15rem;">
          ${isDark ? "☀️" : "🌙"}
        </button>
        <div class="nav-dropdown">
          <button class="nav-button" data-action="nav-dropdown-toggle">Practice ▼</button>
          <div class="nav-dropdown-menu${state.dropdownOpen ? ' open' : ''}">
            <a class="nav-dropdown-item" href="/sql">SQL Practice</a>
            <a class="nav-dropdown-item" href="/lld">LLD Practice</a>
            <a class="nav-dropdown-item active" href="/hld">HLD Practice</a>
          </div>
        </div>
      </div>
    </header>
  `;
}

function renderError() {
  return `
    <div class="notice">
      <span>${escapeHtml(state.error)}</span>
      <button data-action="clear-error">Dismiss</button>
    </div>
  `;
}

function renderPractice() {
  if (state.loading && !state.lesson) {
    return `<section class="sql-shell"><div class="sql-workspace"><div class="hld-empty">Loading HLD practice.</div></div></section>`;
  }
  if (!state.lesson) {
    return `<section class="sql-shell"><div class="sql-workspace"><div class="hld-empty">Loading lessons.</div></div></section>`;
  }

  return `
    <section class="sql-shell">
      ${renderSidebar()}
      ${renderWorkspace()}
    </section>
  `;
}

function renderSidebar() {
  return `
    <aside class="sql-sidebar" aria-label="HLD chapters">
      <div class="sql-sidebar-head">
        <p class="eyebrow">HLD Practice</p>
        <h2>Chapters</h2>
      </div>
      <div class="sql-chapter-list">
        ${(() => {
          const groups = {
            "Core Concepts": [],
            "Common Patterns": [],
            "Key Technologies": [],
            "Advanced Topics": [],
            "Problem Breakdowns": []
          };
          for (const lesson of state.lessons) {
            const badge = lesson.badge || "";
            if (badge.includes("Core")) {
              groups["Core Concepts"].push(lesson);
            } else if (badge.includes("Pattern")) {
              groups["Common Patterns"].push(lesson);
            } else if (badge.includes("Tech")) {
              groups["Key Technologies"].push(lesson);
            } else if (badge.includes("Advanced")) {
              groups["Advanced Topics"].push(lesson);
            } else {
              groups["Problem Breakdowns"].push(lesson);
            }
          }
          return Object.entries(groups)
            .filter(([group, lessons]) => lessons.length > 0)
            .map(([group, lessons]) => `
              <div class="sql-chapter-group">
                <div class="sql-chapter-group-title">${escapeHtml(group)}</div>
                ${lessons.map(lesson => {
                  const solved = solvedCountForLesson(lesson.id);
                  const totalTime = totalLessonTime(lesson.id);
                  return `
                    <button class="sql-chapter ${state.lesson?.id === lesson.id ? "active" : ""}" data-action="hld-lesson" data-lesson-id="${escapeHtml(lesson.id)}">
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

function renderWorkspace() {
  const task = currentTask();
  return `
    <section class="sql-workspace">
      <div class="sql-lesson-head hld-workspace-head">
        <div class="hld-workspace-head-copy">
          <p class="eyebrow">${escapeHtml(state.lesson.badge || "Chapter")} ${state.lesson.number}</p>
          <h2>${escapeHtml(state.lesson.title)}</h2>
          <p>${escapeHtml(state.lesson.overview)}</p>
        </div>
        <div class="hld-lesson-tools">
          <div class="sql-chapter-timer-block${state.chapterStoppedMs != null ? " stopped" : ""}">
            <span class="sql-timer-icon">⏱</span>
            <span class="sql-timer-value" data-hld-chapter-timer>${formatElapsed(chapterElapsedMs())}</span>
            <button class="sql-timer-reset" data-action="hld-reset-lesson" title="Reset chapter progress">↻</button>
          </div>
          <div class="hld-focus-pills">
            ${state.lesson.focus.map((item) => `<span class="pill">${escapeHtml(item)}</span>`).join("")}
            ${state.lesson.notesUrl ? `<a class="notes-link" href="${escapeHtml(state.lesson.notesUrl)}" target="_blank" rel="noreferrer">📖 Notes</a>` : ""}
          </div>
        </div>
      </div>
      <div class="sql-grid">
        <div class="hld-left">
          ${renderOverviewPanel()}
        </div>
        <div class="sql-right">
          ${renderTaskList()}
          ${task ? renderTaskPanel(task) : ""}
          ${task ? renderResultPanel(task) : ""}
        </div>
      </div>
    </section>
  `;
}

function renderOverviewPanel() {
  const solved = solvedCountForLesson(state.lesson.id);
  const total = state.lesson.tasks.length;
  const progressPercent = total > 0 ? Math.round((solved / total) * 100) : 0;

  return `
    <div class="sql-panel">
      <h3>Chapter Overview</h3>
      <div class="sql-progress-bar">
        <div class="sql-progress-bar-fill" style="width: ${progressPercent}%;"></div>
      </div>
      <div class="hld-overview-grid" style="margin-top: 14px;">
        <div class="hld-stat">
          <b>${solved} / ${total}</b>
          <span>Exercises Completed</span>
        </div>
        <div class="hld-stat">
          <b>${progressPercent}%</b>
          <span>Total Score</span>
        </div>
      </div>
    </div>
  `;
}

function renderTaskList() {
  return `
    <div class="sql-panel">
      <h3>Exercises</h3>
      <div class="sql-task-list">
        ${state.lesson.tasks
          .map((task, index) => {
            const isSolved = state.solved[state.lesson.id]?.[task.id] || false;
            const isActive = state.selectedTaskId === task.id;
            const orderNum = index + 1;
            return `
              <button class="sql-task ${isActive ? "active" : ""} ${isSolved ? "solved" : ""}" data-action="hld-task" data-task-id="${escapeHtml(task.id)}">
                <span>${orderNum}</span>
                <b>Task ${orderNum}</b>
                <small>${escapeHtml(task.difficulty)}</small>
              </button>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
}

function renderTaskPanel(task) {
  const isSolved = state.solved[state.lesson.id]?.[task.id] || false;
  const currentResp = currentAnswer(state.lesson.id, task.id);
  const correctOptionIndex = state.check?.expectedIndex;

  return `
    <div class="sql-panel">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3 style="margin: 0;">Question Prompt</h3>
        <span class="pill task-kind-pill" style="font-size: 0.72rem;">${escapeHtml(task.difficulty)}</span>
      </div>
      <p style="font-size: 1.05rem; line-height: 1.5; color: var(--ink); margin: 0 0 16px 0; font-weight: 500;">
        ${escapeHtml(task.prompt)}
      </p>
      <div class="quiz-options">
        ${task.options
          .map((option, idx) => {
            const isSelected = state.selectedAnswer === idx;
            const letter = String.fromCharCode(65 + idx);
            let optionClass = "";

            if (state.check) {
              if (idx === correctOptionIndex) {
                optionClass = "correct";
              } else if (isSelected) {
                optionClass = "wrong";
              }
            } else if (isSelected) {
              optionClass = "selected";
            }

            return `
              <button class="quiz-option ${optionClass}" data-action="hld-select-option" data-option-index="${idx}">
                <div class="quiz-option-key">${letter}</div>
                <div style="line-height: 1.45; font-weight: 450;">${escapeHtml(option)}</div>
              </button>
            `;
          })
          .join("")}
      </div>
      <div class="quiz-actions" style="margin-top: 20px;">
        ${!state.check || !state.check.correct ? `
          <button class="sql-button primary" data-action="hld-check" ${state.selectedAnswer === null || state.loading ? "disabled" : ""}>
            ${state.loading ? "Verifying..." : "Check Answer"}
          </button>
        ` : ""}
        ${state.check && state.check.correct ? `
          <button class="sql-button primary" data-action="hld-next">Next Exercise →</button>
        ` : ""}
      </div>
    </div>
  `;
}

function renderResultPanel(task) {
  const isSolved = state.solved[state.lesson.id]?.[task.id] || false;
  if (!state.check) {
    return "";
  }

  const isCorrect = state.check.correct;

  return `
    <div class="result-stack">
      <div class="result-card ${isCorrect ? "correct" : "wrong"}" style="border: 1px solid ${isCorrect ? "rgba(16, 185, 129, 0.3)" : "rgba(215, 38, 61, 0.22)"}; background: ${isCorrect ? "rgba(16, 185, 129, 0.04)" : "rgba(215, 38, 61, 0.03)"}">
        <h3 style="color: ${isCorrect ? "#10b981" : "#d7263d"}; font-weight: 700; margin-bottom: 8px;">
          ${isCorrect ? "✓ Correct!" : "✗ Incorrect"}
        </h3>
        <p style="line-height: 1.55; color: var(--ink); margin: 0; font-size: 0.98rem; font-weight: 450;">
          ${escapeHtml(state.check.explanation)}
        </p>
      </div>
    </div>
  `;
}

window.addEventListener("click", handleAction);
window.addEventListener("popstate", () => {
  state.selectedLessonId = getHldLessonId();
  loadLesson(state.selectedLessonId, false);
});

loadIndex();
