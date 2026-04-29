# CustomModel Trainer — Phase 1 Starter

CustomModel Trainer is a no-code AI model training platform. This Phase 1 starter implements the foundation MVP:

- FastAPI backend with JWT authentication
- PostgreSQL schema for users, models, datasets, jobs, versions, feedback, API keys, and usage logs
- SQLAlchemy 2.x models and Alembic migration
- Next.js App Router frontend with landing, signup, login, dashboard, and create-model flow
- Docker Compose for web, API, Postgres, Redis, and MinIO

## Run locally with Docker

```bash
cp .env.example .env
# edit API_SECRET_KEY before real use
# macOS/Linux: openssl rand -hex 32

docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001

## Run backend only

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export API_DATABASE_URL="postgresql+psycopg://custommodel:custommodel@localhost:5432/custommodel_trainer"
export API_SECRET_KEY="$(openssl rand -hex 32)"
export API_CORS_ORIGINS="http://localhost:3000"
alembic upgrade head
uvicorn app.main:app --reload
```

## Run frontend only

```bash
cd apps/web
npm install
npm run dev
```

## Phase 1 API smoke test

```bash
curl http://localhost:8000/api/v1/health
```

Create a user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Password123!","full_name":"Demo User"}'
```

## Sample model payload

```json
{
  "name": "Support Answer Bot",
  "description": "Answers customer questions using our support examples.",
  "category": "text_to_text",
  "visibility": "private",
  "icon_url": null,
  "improve_from_feedback": true
}
```
