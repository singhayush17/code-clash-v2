const state = {
  lessons: [],
  lesson: null,
  selectedLessonId: getLldLessonId(),
  selectedTaskId: "",
  loading: false,
  dropdownOpen: false,
  error: "",
  check: null,
  runResult: null,
  showSolution: false,
  editorValue: "",
  selectedAnswer: null,
  solved: loadJson("codeClashLldSolved"),
  drafts: loadJson("codeClashLldDrafts"),
  quizAnswers: loadJson("codeClashLldQuizAnswers"),
  taskTimes: loadJson("codeClashLldTaskTimes"),
  chapterStartTime: null,
  chapterStoppedMs: null,
  questionStartTime: null,
  timerId: null,
};

const app = document.querySelector("#lld-app");

function getLldLessonId() {
  const match = window.location.pathname.match(/^\/lld\/([^/]+)/);
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
  saveJson("codeClashLldSolved", state.solved);
}

function saveDrafts() {
  saveJson("codeClashLldDrafts", state.drafts);
}

function saveQuizAnswers() {
  saveJson("codeClashLldQuizAnswers", state.quizAnswers);
}

function saveTaskTimes() {
  saveJson("codeClashLldTaskTimes", state.taskTimes);
}

function saveLastPosition() {
  saveJson("codeClashLldPosition", {
    lessonId: state.selectedLessonId,
    taskId: state.selectedTaskId,
  });
}

function loadLastPosition() {
  return loadJson("codeClashLldPosition");
}

function currentTask() {
  return state.lesson?.tasks.find((task) => task.id === state.selectedTaskId) || null;
}

function currentDraft(lessonId, taskId) {
  return state.drafts[lessonId]?.[taskId] ?? null;
}

function currentAnswer(lessonId, taskId) {
  return state.quizAnswers[lessonId]?.[taskId] ?? null;
}

function saveCurrentResponse() {
  const task = currentTask();
  const lessonId = state.lesson?.id;
  if (!task || !lessonId) {
    return;
  }

  if (task.kind === "code") {
    state.drafts[lessonId] = state.drafts[lessonId] || {};
    const starter = (task.starter || "").trim();
    const draft = state.editorValue.trim();
    if (draft && draft !== starter) {
      state.drafts[lessonId][task.id] = state.editorValue;
    } else {
      delete state.drafts[lessonId]?.[task.id];
    }
    saveDrafts();
    return;
  }

  state.quizAnswers[lessonId] = state.quizAnswers[lessonId] || {};
  if (state.selectedAnswer == null) {
    delete state.quizAnswers[lessonId]?.[task.id];
  } else {
    state.quizAnswers[lessonId][task.id] = state.selectedAnswer;
  }
  saveQuizAnswers();
}

function restoreTaskResponse() {
  const task = currentTask();
  const lessonId = state.lesson?.id;
  state.check = null;
  state.runResult = null;
  state.showSolution = false;
  state.questionStartTime = Date.now();
  if (!task || !lessonId) {
    state.editorValue = "";
    state.selectedAnswer = null;
    return;
  }

  if (task.kind === "code") {
    state.editorValue = currentDraft(lessonId, task.id) ?? task.starter ?? "";
    state.selectedAnswer = null;
  } else {
    state.selectedAnswer = currentAnswer(lessonId, task.id);
    state.editorValue = "";
  }
  saveLastPosition();
}

function isTaskSolved(taskId) {
  const lessonId = state.lesson?.id;
  return Boolean(lessonId && state.solved[lessonId]?.[taskId]);
}

function markTaskSolved(taskId) {
  const lessonId = state.lesson?.id;
  if (!lessonId) {
    return;
  }
  state.solved[lessonId] = state.solved[lessonId] || {};
  state.solved[lessonId][taskId] = true;
  saveSolved();
}

function solvedCountForLesson(lessonId) {
  const solved = state.solved[lessonId] || {};
  return Object.keys(solved).filter((taskId) => solved[taskId]).length;
}

function recordTaskTime(taskId) {
  const lessonId = state.lesson?.id;
  if (!lessonId || !state.questionStartTime) {
    return;
  }
  const elapsed = Math.floor((Date.now() - state.questionStartTime) / 1000);
  state.taskTimes[lessonId] = state.taskTimes[lessonId] || {};
  if (!state.taskTimes[lessonId][taskId]) {
    state.taskTimes[lessonId][taskId] = elapsed;
    saveTaskTimes();
  }
  if (isLessonComplete()) {
    state.chapterStoppedMs = chapterElapsedMs();
    state.questionStartTime = null;
  }
}

function getTaskTime(lessonId, taskId) {
  return state.taskTimes[lessonId]?.[taskId] || null;
}

function totalLessonTime(lessonId) {
  const values = Object.values(state.taskTimes[lessonId] || {});
  return values.length ? values.reduce((sum, value) => sum + value, 0) : null;
}

function isLessonComplete() {
  if (!state.lesson) {
    return false;
  }
  return state.lesson.tasks.every((task) => isTaskSolved(task.id));
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

function questionElapsedMs() {
  if (!state.questionStartTime) {
    return 0;
  }
  return Date.now() - state.questionStartTime;
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
  if (seconds == null) {
    return "";
  }
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  if (minutes > 0) {
    return `${minutes}m ${remaining}s`;
  }
  return `${remaining}s`;
}

function startTimers() {
  stopTimers();
  state.timerId = window.setInterval(updateTimers, 1000);
}

function stopTimers() {
  if (state.timerId) {
    window.clearInterval(state.timerId);
    state.timerId = null;
  }
}

function updateTimers() {
  const chapter = document.querySelector("[data-lld-chapter-timer]");
  if (chapter) {
    chapter.textContent = formatElapsed(chapterElapsedMs());
  }
  const question = document.querySelector("[data-lld-question-timer]");
  if (question) {
    question.textContent = formatElapsed(questionElapsedMs());
  }
}

function nextTaskId() {
  const tasks = state.lesson?.tasks || [];
  const currentIndex = tasks.findIndex((task) => task.id === state.selectedTaskId);
  if (currentIndex === -1) {
    return "";
  }
  const laterUnsolved = tasks.slice(currentIndex + 1).find((task) => !isTaskSolved(task.id));
  return laterUnsolved?.id || tasks[currentIndex + 1]?.id || "";
}

function advanceTask() {
  const nextId = nextTaskId();
  if (!nextId) {
    return false;
  }
  state.selectedTaskId = nextId;
  restoreTaskResponse();
  return true;
}

async function loadIndex() {
  if (state.loading || state.lessons.length) {
    return;
  }
  state.loading = true;
  state.error = "";
  render();
  try {
    const response = await fetch("/api/lld/lessons");
    const payload = await response.json();
    state.lessons = payload.lessons || [];
    const last = loadLastPosition();
    const lessonId = state.selectedLessonId || last.lessonId || state.lessons[0]?.id || "";
    if (lessonId) {
      await loadLesson(lessonId, false);
    }
  } catch (error) {
    state.error = error.message || "Could not load LLD lessons.";
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
  state.runResult = null;
  state.showSolution = false;
  render();
  try {
    const response = await fetch(`/api/lld/lessons/${encodeURIComponent(lessonId)}`);
    const payload = await response.json();
    state.lesson = payload.lesson;
    state.selectedLessonId = payload.lesson.id;
    const route = `/lld/${payload.lesson.id}`;
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
    state.chapterStartTime = Date.now();
    state.chapterStoppedMs = null;
    startTimers();
    restoreTaskResponse();
  } catch (error) {
    state.error = error.message || "Could not load this chapter.";
  } finally {
    state.loading = false;
    render();
  }
}

function resetLessonProgress() {
  const lessonId = state.lesson?.id;
  if (!lessonId) {
    return;
  }
  delete state.solved[lessonId];
  delete state.taskTimes[lessonId];
  delete state.drafts[lessonId];
  delete state.quizAnswers[lessonId];
  saveSolved();
  saveTaskTimes();
  saveDrafts();
  saveQuizAnswers();
  state.chapterStartTime = Date.now();
  state.chapterStoppedMs = null;
  state.selectedTaskId = state.lesson.tasks[0]?.id || "";
  restoreTaskResponse();
  startTimers();
}

function resetCurrentTask() {
  const task = currentTask();
  if (!task) {
    return;
  }
  if (task.kind === "code") {
    state.editorValue = task.starter || "";
  } else {
    state.selectedAnswer = null;
  }
  saveCurrentResponse();
  state.runResult = null;
  state.check = null;
  state.showSolution = false;
}

async function runCode() {
  const task = currentTask();
  if (!state.lesson || !task || task.kind !== "code") {
    return;
  }
  state.error = "";
  state.runResult = null;
  state.check = null;
  render();
  try {
    const response = await fetch("/api/lld/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lessonId: state.lesson.id,
        taskId: task.id,
        code: state.editorValue,
      }),
    });
    const data = await response.json();
    if (!data.ok) {
      throw new Error(data.error || "Run failed.");
    }
    state.runResult = data;
  } catch (error) {
    state.error = error.message || "Run failed.";
  } finally {
    render();
  }
}

async function checkCurrentTask() {
  const task = currentTask();
  if (!state.lesson || !task) {
    return;
  }
  state.error = "";
  let advanced = false;
  try {
    const payload = {
      lessonId: state.lesson.id,
      taskId: task.id,
    };
    if (task.kind === "quiz") {
      payload.answer = state.selectedAnswer;
    } else {
      payload.code = state.editorValue;
    }
    const response = await fetch("/api/lld/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!data.ok) {
      throw new Error(data.error || "Check failed.");
    }
    state.check = data;
    if (data.correct) {
      markTaskSolved(task.id);
      recordTaskTime(task.id);
      if (task.kind === "code" && state.lesson?.id) {
        delete state.drafts[state.lesson.id]?.[task.id];
        saveDrafts();
      }
      advanced = advanceTask();
    }
  } catch (error) {
    state.error = error.message || "Check failed.";
  } finally {
    if (!advanced) {
      render();
    } else {
      render();
    }
  }
}

function render() {
  const editor = document.querySelector("#lldEditor");
  const hadFocus = editor && document.activeElement === editor;
  const selection = hadFocus
    ? { start: editor.selectionStart, end: editor.selectionEnd }
    : null;

  app.innerHTML = `
    ${renderTopbar()}
    ${state.error ? renderError() : ""}
    <main class="shell">
      ${renderPractice()}
    </main>
    <p class="lld-footnote">One pattern per chapter, plus focused machine-coding labs for the practical interview rounds.</p>
  `;

  if (selection) {
    restoreEditorSelection(selection);
  }
}

function renderTopbar() {
  return `
    <header class="topbar lld-topbar">
      <div class="brand" style="cursor: pointer;" onclick="window.location.href='/'">
        <div class="lld-brand-mark">LLD</div>
        <div>
          <h1>Code Clash</h1>
          <p>Python low-level design practice with patterns, quizzes, and machine-coding drills.</p>
        </div>
      </div>
      <div class="nav-links">
        <div class="nav-dropdown">
          <button class="nav-button" data-action="nav-dropdown-toggle">Practice ▼</button>
          <div class="nav-dropdown-menu${state.dropdownOpen ? ' open' : ''}">
            <a class="nav-dropdown-item" href="/sql">SQL Practice</a>
            <a class="nav-dropdown-item active" href="/lld">LLD Practice</a>
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
    return `<section class="sql-shell"><div class="sql-workspace"><div class="lld-empty">Loading LLD practice.</div></div></section>`;
  }
  if (!state.lesson) {
    return `<section class="sql-shell"><div class="sql-workspace"><div class="lld-empty">Loading lessons.</div></div></section>`;
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
    <aside class="sql-sidebar" aria-label="LLD chapters">
      <div class="sql-sidebar-head">
        <p class="eyebrow">LLD Practice</p>
        <h2>Pattern Kits</h2>
      </div>
      <div class="sql-chapter-list">
        ${state.lessons
          .map((lesson) => {
            const solved = solvedCountForLesson(lesson.id);
            const totalTime = totalLessonTime(lesson.id);
            return `
              <button class="sql-chapter ${state.lesson?.id === lesson.id ? "active" : ""}" data-action="lld-lesson" data-lesson-id="${escapeHtml(lesson.id)}">
                <span>${lesson.number}</span>
                <b>${escapeHtml(lesson.title)}</b>
                <small>${escapeHtml(lesson.badge || "Kit")} · ${solved}/${lesson.taskCount}${totalTime != null ? ` · ${formatElapsedCompact(totalTime)}` : ""}</small>
              </button>
            `;
          })
          .join("")}
      </div>
    </aside>
  `;
}

function renderWorkspace() {
  const task = currentTask();
  return `
    <section class="sql-workspace">
      <div class="sql-lesson-head lld-workspace-head">
        <div class="lld-workspace-head-copy">
          <p class="eyebrow">${escapeHtml(state.lesson.badge || "Kit")} ${state.lesson.number}</p>
          <h2>${escapeHtml(state.lesson.title)}</h2>
          <p>${escapeHtml(state.lesson.overview)}</p>
        </div>
        <div class="lld-lesson-tools">
          <div class="sql-chapter-timer-block${state.chapterStoppedMs != null ? " stopped" : ""}">
            <span class="sql-timer-icon">⏱</span>
            <span class="sql-timer-value" data-lld-chapter-timer>${formatElapsed(chapterElapsedMs())}</span>
            <button class="sql-timer-reset" data-action="lld-reset-lesson" title="Reset chapter progress">↻</button>
          </div>
          <div class="lld-focus-pills">
            ${state.lesson.focus.map((item) => `<span class="pill">${escapeHtml(item)}</span>`).join("")}
          </div>
        </div>
      </div>
      <div class="sql-grid">
        <div class="lld-left">
          ${renderOverviewPanel()}
          ${renderPatternPanel()}
        </div>
        <div class="sql-right">
          ${renderTaskList()}
          ${task ? renderTaskPanel(task) : ""}
          ${task ? renderResponsePanel(task) : ""}
          ${renderResultPanel(task)}
        </div>
      </div>
    </section>
  `;
}

function renderOverviewPanel() {
  const task = currentTask();
  const pattern = state.lesson.patterns?.[0];
  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>${pattern ? "Pattern Brief" : "Design Brief"}</h3>
        <span class="pill strong">${solvedCountForLesson(state.lesson.id)}/${state.lesson.tasks.length} solved</span>
      </div>
      <div class="task-summary">
        ${pattern ? `<div class="lld-meta-pills"><span class="pill strong">${escapeHtml(pattern.name)}</span><span class="pill">${escapeHtml(pattern.family)}</span></div>` : ""}
        <p class="task-summary-copy">${escapeHtml(state.lesson.overview)}</p>
        ${task ? `<p class="task-summary-copy"><strong>Current drill:</strong> ${escapeHtml(task.prompt)}</p>` : ""}
      </div>
    </section>
  `;
}

function renderPatternPanel() {
  if (!state.lesson.patterns.length) {
    return `
      <section class="sql-panel">
        <div class="sql-panel-head">
          <h3>How To Use This Kit</h3>
        </div>
        <div class="task-summary">
          <p class="task-summary-copy">Start by naming the change axis, then keep responsibilities small and inject the volatile behavior instead of hard-coding it.</p>
        </div>
      </section>
    `;
  }

  const pattern = state.lesson.patterns[0];
  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>When To Reach For It</h3>
      </div>
      <article class="pattern-card">
        <div class="pattern-head">
          <b>${escapeHtml(pattern.name)}</b>
          <span class="pill">${escapeHtml(pattern.family)}</span>
        </div>
        <p><strong>Intent:</strong> ${escapeHtml(pattern.intent)}</p>
        <p><strong>Signals:</strong> ${escapeHtml(pattern.signals)}</p>
        <p><strong>Watch out:</strong> ${escapeHtml(pattern.pitfall)}</p>
        <p><strong>Python move:</strong> ${escapeHtml(pattern.pythonTip)}</p>
      </article>
    </section>
  `;
}

function renderTaskList() {
  return `
    <section class="sql-panel task-panel">
      <div class="sql-panel-head">
        <h3>Exercises</h3>
        <span class="pill strong">${solvedCountForLesson(state.lesson.id)}/${state.lesson.tasks.length} solved</span>
      </div>
      <div class="sql-task-list">
        ${state.lesson.tasks
          .map((task, index) => {
            const solveTime = getTaskTime(state.lesson.id, task.id);
            return `
              <button class="sql-task ${task.id === state.selectedTaskId ? "active" : ""} ${isTaskSolved(task.id) ? "solved" : ""}" data-action="lld-task" data-task-id="${escapeHtml(task.id)}">
                <span>${isTaskSolved(task.id) ? "✓" : index + 1}</span>
                <b>${escapeHtml(task.prompt)}</b>
                <small>
                  ${escapeHtml(task.kind)} · ${escapeHtml(task.difficulty)}${solveTime != null ? ` · ${formatElapsedCompact(solveTime)}` : ""}
                </small>
              </button>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderTaskPanel(task) {
  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>${escapeHtml(task.prompt)}</h3>
        <div class="lld-meta-pills">
          <span class="pill task-kind-pill">${escapeHtml(task.kind)}</span>
          <span class="pill">${escapeHtml(task.difficulty)}</span>
          <div class="sql-question-timer-block">
            <span class="sql-timer-icon">⏱</span>
            <span class="sql-timer-value" data-lld-question-timer>${formatElapsed(questionElapsedMs())}</span>
          </div>
        </div>
      </div>
      <div class="task-summary">
        ${task.tags?.length ? `<div class="lld-meta-pills">${task.tags.map((tag) => `<span class="pill">${escapeHtml(tag)}</span>`).join("")}</div>` : ""}
        ${task.hint ? `<p class="task-summary-copy">${escapeHtml(task.hint)}</p>` : ""}
        ${task.checklist?.length ? `<ul class="brief-list">${task.checklist.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
      </div>
    </section>
  `;
}

function renderResponsePanel(task) {
  if (task.kind === "quiz") {
    return renderQuizPanel(task);
  }
  return renderCodePanel(task);
}

function renderQuizPanel(task) {
  const labels = ["A", "B", "C", "D"];
  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>Answer</h3>
        <div class="quiz-actions">
          <button class="secondary-button compact" data-action="lld-reset-task">Reset</button>
          <button class="primary-button compact" data-action="lld-check">Check</button>
        </div>
      </div>
      <div class="quiz-options">
        ${task.options
          .map((option, index) => {
            const selected = state.selectedAnswer === index;
            const expected = state.check?.expectedIndex === index;
            const wrongSelected = state.check && !state.check.correct && selected && !expected;
            const classes = [
              "quiz-option",
              selected ? "selected" : "",
              state.check?.correct && selected ? "correct" : "",
              state.check && !state.check.correct && expected ? "correct" : "",
              wrongSelected ? "wrong" : "",
            ]
              .filter(Boolean)
              .join(" ");
            return `
              <button class="${classes}" data-action="lld-option" data-option-index="${index}">
                <span class="quiz-option-key">${labels[index]}</span>
                <span>${escapeHtml(option)}</span>
              </button>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderCodePanel(task) {
  return `
    <section class="sql-panel editor-panel">
      <div class="sql-panel-head">
        <h3>Editor</h3>
        <div class="lld-editor-actions">
          <button class="secondary-button compact" data-action="lld-solution">${state.showSolution ? "Hide Reference" : "Reference"}</button>
          <button class="secondary-button compact" data-action="lld-reset-task">Reset</button>
          <button class="secondary-button compact" data-action="lld-run">Run</button>
          <button class="primary-button compact" data-action="lld-check">Check</button>
        </div>
      </div>
      <textarea id="lldEditor" spellcheck="false">${escapeHtml(state.editorValue)}</textarea>
    </section>
  `;
}

function renderResultPanel(task) {
  const shouldShowSolution = state.showSolution && task?.kind === "code";
  if (!state.runResult && !state.check && !shouldShowSolution) {
    return `<section class="sql-panel"><div class="empty compact-empty">Run code, check an answer, or open the reference implementation to compare approaches.</div></section>`;
  }

  return `
    <section class="sql-panel">
      <div class="sql-panel-head">
        <h3>Feedback</h3>
        ${state.check ? `<span class="pill ${state.check.correct ? "strong" : "wrong-pill"}">${state.check.correct ? "Solved" : "Needs work"}</span>` : ""}
      </div>
      <div class="result-stack">
        ${renderCheckCard(task)}
        ${renderRunCard()}
        ${shouldShowSolution ? renderSolutionCard(task) : ""}
      </div>
    </section>
  `;
}

function renderCheckCard(task) {
  if (!state.check) {
    return "";
  }
  if (task?.kind === "quiz") {
    return `
      <article class="result-card">
        <h3>${escapeHtml(state.check.message || "")}</h3>
        <p>${escapeHtml(state.check.explanation || "")}</p>
        ${state.check.solution ? `<p><strong>Reference answer:</strong> ${escapeHtml(state.check.solution)}</p>` : ""}
      </article>
    `;
  }
  return `
    <article class="result-card">
      <h3>${escapeHtml(state.check.message || "")}</h3>
      ${state.check.summary ? `<p>${escapeHtml(state.check.summary)}</p>` : ""}
      ${state.check.checks?.length ? `
        <div class="check-list">
          ${state.check.checks
            .map(
              (item) => `
                <div class="check-item ${item.ok ? "ok" : "bad"}">
                  <b>${item.ok ? "Pass" : "Miss"}</b>
                  <span>${escapeHtml(item.message)}</span>
                </div>
              `,
            )
            .join("")}
        </div>
      ` : ""}
      ${state.check.stdout ? `<pre>${escapeHtml(state.check.stdout)}</pre>` : ""}
      ${state.check.stderr ? `<pre>${escapeHtml(state.check.stderr)}</pre>` : ""}
    </article>
  `;
}

function renderRunCard() {
  if (!state.runResult) {
    return "";
  }
  return `
    <article class="result-card">
      <h3>${escapeHtml(state.runResult.message || "")}</h3>
      ${state.runResult.stdout ? `<pre>${escapeHtml(state.runResult.stdout)}</pre>` : `<p>No stdout.</p>`}
      ${state.runResult.stderr ? `<pre>${escapeHtml(state.runResult.stderr)}</pre>` : ""}
    </article>
  `;
}

function renderSolutionCard(task) {
  if (!task || task.kind !== "code") {
    return "";
  }
  const solution = task.reference || state.check?.solution || "";
  return `
    <article class="result-card solution-block">
      <h3>Reference Implementation</h3>
      <pre>${escapeHtml(solution)}</pre>
    </article>
  `;
}

function restoreEditorSelection(selection) {
  const editor = document.querySelector("#lldEditor");
  if (!editor) {
    return;
  }
  editor.focus();
  const start = Math.min(selection.start, editor.value.length);
  const end = Math.min(selection.end, editor.value.length);
  editor.setSelectionRange(start, end);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("click", async (event) => {
  if (!event.target.closest(".nav-dropdown") && state.dropdownOpen) {
    state.dropdownOpen = false;
    render();
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

  if (action === "clear-error") {
    state.error = "";
    render();
  }

  if (action === "lld-lesson") {
    await loadLesson(button.dataset.lessonId);
  }

  if (action === "lld-task") {
    saveCurrentResponse();
    state.selectedTaskId = button.dataset.taskId;
    restoreTaskResponse();
    render();
  }

  if (action === "lld-option") {
    state.selectedAnswer = Number(button.dataset.optionIndex);
    saveCurrentResponse();
    render();
  }

  if (action === "lld-reset-task") {
    resetCurrentTask();
    render();
  }

  if (action === "lld-reset-lesson") {
    resetLessonProgress();
    render();
  }

  if (action === "lld-run") {
    await runCode();
  }

  if (action === "lld-check") {
    await checkCurrentTask();
  }

  if (action === "lld-solution") {
    state.showSolution = !state.showSolution;
    render();
  }
});

document.addEventListener("input", (event) => {
  if (event.target?.id === "lldEditor") {
    state.editorValue = event.target.value;
    saveCurrentResponse();
    state.runResult = null;
    state.check = null;
  }
});

document.addEventListener("keydown", (event) => {
  if (event.target?.id === "lldEditor" && (event.metaKey || event.ctrlKey) && event.key === "Enter") {
    if (event.shiftKey) {
      checkCurrentTask();
    } else {
      runCode();
    }
  }
});

window.addEventListener("popstate", () => {
  state.selectedLessonId = getLldLessonId();
  if (state.selectedLessonId && state.selectedLessonId !== state.lesson?.id) {
    loadLesson(state.selectedLessonId, false);
  } else {
    render();
  }
});

render();
loadIndex();
