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
| Applicant | `sohum`     | `sohum`     |

The `sohum` account is seeded with older sample applications on the first two jobs (so “top 5” lists are dominated by fresher demo candidates). Additional demo applicants (`taylor`, `sam`, `riley`, `jordan`, `morgan`, `alex`, `casey` on Software Dev; `priya`, `dev` on Product Manager) are added when missing—password equals username for each. Delete `portal.sqlite` to re-run all seeds.

**HR + OpenAI:** Set `OPENAI_API_KEY` (and optional `OPENAI_MODEL`, default `gpt-5-nano`; use `gpt-4o-mini` if your key does not have access to that model) in `backend/.env`. HR can use **Summarize & recommend top match** on a job, which calls `POST /api/jobs/{id}/summarize-resumes` and sends the job title/description plus extracted text from the five most recent resumes to OpenAI. The response includes per-applicant summaries and a **top pick** with a short justification tied to the role. Jobs with no applicants return empty summaries without calling the API.

**Keeping API keys safe:** The key stays on the server only (read from env / `.env`). It is not exposed to the browser, not included in API JSON responses, and summarization errors return a generic message to clients while details go to server logs. `.env` is gitignored—use `.env.example` as a template. If a key is ever committed or leaked, revoke it in the [OpenAI API keys](https://platform.openai.com/api-keys) dashboard and create a new one.

**Signup:** `POST /api/auth/register` with `username`, `password`, and `role: "applicant"`. There is no email field and no verification step—any non-empty username and password are accepted after trimming the username.

**Login:** `POST /api/auth/login` with `username`, `password`, and `role` (`hr` or `applicant`).

**Jobs (authenticated):** `GET /api/jobs` lists open roles with full descriptions; `GET /api/jobs/{id}` returns one role. Five seed jobs are inserted when the `jobs` table is empty (Software Dev, Product Manager, ML Engineer, HR, Financial Analyst).

**Applications:** Applicants `POST /api/jobs/{id}/resume` (multipart `file`, types `.pdf`/`.doc`/`.docx`/`.txt`, max 5MB). `GET /api/jobs/{id}/my-application` returns the current user’s submission. HR `GET /api/jobs/{id}/applicants` returns up to five most recent applicants per role. `GET /api/applications/{id}/resume` downloads the file (HR or the owning applicant). Resume files live under `data/resumes/` next to the SQLite file.

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
