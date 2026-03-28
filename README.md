# Prisha Company — application portal

## Backend (Python)

SQLite database file: `backend/data/portal.sqlite` (created on first run). Override with env `PORTAL_DB_PATH` (used by tests). If you still have an older DB that used email as the login field, delete `portal.sqlite` once so the app can re-seed demo users (`hr` / `hr` and `applicant` / `applicant`).

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set JWT_SECRET to a random string at least 16 characters long.
uvicorn app.main:app --reload --host 127.0.0.1 --port 3001
```

- API: [http://127.0.0.1:3001/api/health](http://127.0.0.1:3001/api/health)
- Interactive docs: [http://127.0.0.1:3001/docs](http://127.0.0.1:3001/docs)

**Demo logins** (seeded on startup: `hr` and `applicant` only when the DB has no users in that role; `prisha` is added whenever that username is missing):

| Role      | Username    | Password    |
| --------- | ----------- | ----------- |
| HR        | `prisha`    | `prisha`    |
| HR        | `hr`        | `hr`        |
| Applicant | `applicant` | `applicant` |

**Signup:** `POST /api/auth/register` with `username`, `password`, and `role: "applicant"`. There is no email field and no verification step—any non-empty username and password are accepted after trimming the username.

**Login:** `POST /api/auth/login` with `username`, `password`, and `role` (`hr` or `applicant`).

Set `FRONTEND_ORIGIN` in `.env` to match your frontend dev server (default `http://localhost:5173`).

## Frontend (React + Vite)

Run the API first (port **3001**). The dev server proxies `/api` to the backend so you avoid CORS issues.

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). For production builds without the proxy, set `VITE_API_URL` to your API base URL (e.g. `http://127.0.0.1:3001`).

### Tests

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Each test uses a temporary database via `PORTAL_DB_PATH`; no email or external services are required.

## GitHub

This folder is its **own** git repository (separate from a parent `git` repo if one exists higher on disk).

After [installing the GitHub CLI](https://cli.github.com/) (`brew install gh`), sign in and create the remote in one step from the project root:

```bash
cd /Users/pbobde/personal/jobapplication
gh auth login
gh repo create jobapplication --public --source=. --remote=origin --push
```

Use any repo name you like instead of `jobapplication`. If the repository already exists on GitHub, add it and push:

```bash
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```
