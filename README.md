# test-0002

Building Magazine

## Local development

For automated setup (dependencies, env file, database, and systemd unit), see
[`install.md`](install.md).

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Database migrations (Alembic)

From the `backend` directory:

```bash
alembic upgrade head
```

To target a specific database, set `DATABASE_URL` (defaults to
`sqlite:///./app.db`):

```bash
DATABASE_URL=sqlite:////absolute/path/to/app.db alembic upgrade head
```

### Frontend (React + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

Vite will serve the app at the URL printed in the terminal (typically `http://localhost:5173`).
