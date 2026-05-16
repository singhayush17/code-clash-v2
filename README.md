# Code Clash

Code Clash is a profile-less 1v1 MCQ battle app for DSA, CN, OOPS, OS, System Design, Core CS, and aptitude prep. This version runs locally with a FastAPI server, WebSockets, an in-memory game loop, and an updateable 300-question JSON bank.

## Live App

Code Clash is hosted on Render at [https://code-clash-3uwa.onrender.com/](https://code-clash-3uwa.onrender.com/).

## What Works Now

- Create a private 1v1 room and share `/room/{code}`.
- Invite links expire after 30 minutes while waiting.
- Find a random online player through in-memory matchmaking.
- Choose 30 seconds or 1 to 10 minutes for invite, matchmaking, or solo battles.
- Choose a battle type: All topics, one topic, or a custom topic mix such as DSA + System Design.
- Play solo with the same strict timed format.
- Server-authoritative scoring: 1 point per correct answer, no negatives, no skips, highest score wins.
- Review your own answered questions at the end of the current game, including your pick and the correct option. Reviews stay in memory only for the current room.
- **Comprehensive SQL Practice:** A massive 49-chapter interactive curriculum covering everything from basic `SELECT` to advanced `WINDOW` functions, CTEs, Joins, DDL Constraints, Views, Indexes, and an interactive SQL Injection "Hacker Mode".
- **LLD Practice Track:** A dedicated Python Low-Level Design practice track featuring design-pattern drills, scenario-heavy quizzes, and machine-coding labs.
- Random usernames and generated SVG avatars.
- Adaptive questions: players start on easy questions and move toward medium/hard as they answer more and build score/streak.
- 300 starter MCQs across all supported subjects, with balanced correct-answer positions across A, B, C, and D.
- At least 42 questions are available in each supported subject.
- No accounts, no profiles, no match history, no replaying old games.
- Update questions by editing `data/questions.json` and reloading the bank.

## Run Locally

You can run the server easily using the included script:

```bash
./run.sh
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Practice routes:

- [http://127.0.0.1:8000/sql](http://127.0.0.1:8000/sql)
- [http://127.0.0.1:8000/lld](http://127.0.0.1:8000/lld)

For 1v1 testing, open two browser windows. Create a link in one window and open it in the other, or click "Find Random Player" in both.

## Question Bank

Questions live in [`data/questions.json`](data/questions.json). Each item uses:

```json
{
  "id": "dsa-e-001",
  "category": "DSA",
  "difficulty": "easy",
  "prompt": "Question text",
  "options": ["A", "B", "C", "D"],
  "answerIndex": 0,
  "explanation": "Short answer explanation"
}
```

After editing the file while the server is running:

```bash
curl -X POST http://127.0.0.1:8000/api/admin/reload-questions
```

For production, protect this reload endpoint with an admin token or remove it and reload only on deploy.
Set `ADMIN_TOKEN` to require `X-Admin-Token` on reload requests:

```bash
ADMIN_TOKEN=change-me uvicorn app.main:app --reload
curl -X POST -H "X-Admin-Token: change-me" http://127.0.0.1:8000/api/admin/reload-questions
```

## Free Hosting Roadmap

This app intentionally starts as a single stateless web service:

1. Local MVP, done here
   - Single FastAPI process serves HTML/CSS/JS and WebSocket game traffic.
   - In-memory rooms keep the product profile-less and cheap.
   - No database is needed until profiles, ELO, analytics, or persistent question editing arrive.

2. Free single-service deploy
   - Deploy the same app as one web service.
   - Use one instance only; in-memory matchmaking only works correctly when all players hit the same process.
   - Good for demos, campus use, and early feedback.

3. Better free/near-free realtime architecture
   - Move room state to a coordinator that guarantees both players land in the same room actor.
   - Cloudflare Workers + Durable Objects is the clean long-term fit for global low-latency rooms, but it would mean porting the Python game loop to a Worker/Durable Object model.
   - Keep static assets on the same platform or on any free static host.

4. Question operations
   - Keep JSON for the first admin workflow.
   - Add a private admin page to upload/validate questions.
   - Later move questions to a free database or object store only when non-developer editing becomes necessary.

5. Competitive layer
   - Add anonymous device identity first if needed.
   - Add profiles, ELO, seasons, history, and anti-abuse only after the base battle loop feels good.

## Current Hosting Notes

- Render can run a FastAPI WebSocket app as a free web service, but free services spin down after 15 minutes without inbound traffic and have monthly free instance-hour limits.
- Render supports inbound WebSockets on web services, but free single-instance state can disappear on restart or redeploy.
- Cloudflare Workers Free includes limited Worker usage, and Durable Objects are available on Free/Paid plans; Durable Objects are a strong future fit for stateful multiplayer rooms.

Sources checked April 11, 2026:

- [Render free services](https://render.com/docs/free)
- [Render WebSockets](https://render.com/docs/websocket)
- [Cloudflare Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/)
- [Cloudflare Durable Objects](https://developers.cloudflare.com/durable-objects/)

## Design Docs

- [High-level design](docs/HLD.md)
- [Low-level design](docs/LLD.md)
