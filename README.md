# test-0002

Building Magazine

## Local development

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend (React + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

Vite will serve the app at the URL printed in the terminal (typically `http://localhost:5173`).
