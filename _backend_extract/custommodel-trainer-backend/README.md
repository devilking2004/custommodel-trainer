# CustomModel Trainer Backend

Production-minded FastAPI backend starter for **CustomModel Trainer**.

It includes:

- FastAPI API
- PostgreSQL + SQLAlchemy 2.x ORM
- JWT authentication
- S3-compatible file storage through boto3
- MinIO for local object storage
- Redis + RQ background training jobs
- Dataset validation and Data Readiness Score
- Mock training pipeline with model versioning
- API key creation with hashed key storage
- Mock inference endpoint
- Feedback collection and review
- Retraining request flow
- Usage logs
- Alembic migrations
- Docker Compose
- Pytest smoke tests

## 1. Local setup with Docker

```bash
cp .env.example .env
```

Edit these values in `.env`:

```txt
API_SECRET_KEY=replace-with-openssl-rand-hex-32
API_KEY_PEPPER=replace-with-another-openssl-rand-hex-32
```

Generate secrets:

```bash
openssl rand -hex 32
openssl rand -hex 32
```

Run everything:

```bash
docker compose up --build
```

Open:

```txt
API:            http://localhost:8000
Swagger docs:   http://localhost:8000/docs
MinIO console:  http://localhost:9001
PostgreSQL:     localhost:5432
Redis:          localhost:6379
```

MinIO login:

```txt
username: minioadmin
password: minioadmin
```

## 2. Local setup without Docker

You still need PostgreSQL, Redis, and S3-compatible storage available.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Start a worker in another terminal:

```bash
python -m app.workers.worker
```

## 3. Testing

Run unit/smoke tests:

```bash
pytest
```

Compile Python files:

```bash
python -m compileall app tests
```

## 4. Main API routes

### Auth

```txt
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/users/me
```

### Models

```txt
GET   /api/v1/models
POST  /api/v1/models
GET   /api/v1/models/{model_id}
PATCH /api/v1/models/{model_id}
POST  /api/v1/models/{model_id}/icon
```

### Datasets

```txt
POST /api/v1/models/{model_id}/datasets
GET  /api/v1/models/{model_id}/datasets
GET  /api/v1/datasets/{dataset_id}
POST /api/v1/datasets/{dataset_id}/files
POST /api/v1/datasets/{dataset_id}/validate
GET  /api/v1/datasets/{dataset_id}/readiness
```

### Training and retraining

```txt
POST /api/v1/models/{model_id}/train
POST /api/v1/models/{model_id}/retrain
GET  /api/v1/training-jobs/{job_id}
```

### Versions

```txt
GET  /api/v1/models/{model_id}/versions
POST /api/v1/models/{model_id}/versions/{version_id}/rollback
```

### API keys and inference

```txt
POST   /api/v1/models/{model_id}/api-keys
GET    /api/v1/models/{model_id}/api-keys
DELETE /api/v1/api-keys/{api_key_id}
POST   /api/v1/inference/{model_id}
```

`POST /api/v1/inference/{model_id}` requires:

```txt
X-API-Key: cmt_live_...
```

### Feedback and usage

```txt
GET   /api/v1/models/{model_id}/feedback
POST  /api/v1/models/{model_id}/feedback
POST  /api/v1/inference/{model_id}/feedback
PATCH /api/v1/feedback/{feedback_id}/review
GET   /api/v1/models/{model_id}/usage
```

## 5. Example curl flow

### Signup

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Password123!","full_name":"Demo User"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Create a Text-to-Text model

```bash
MODEL_ID=$(curl -s -X POST http://localhost:8000/api/v1/models \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Customer Support Bot",
    "description":"Answers support questions.",
    "category":"text_to_text",
    "visibility":"private",
    "improve_from_feedback":true
  }' | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

### Create dataset

```bash
DATASET_ID=$(curl -s -X POST http://localhost:8000/api/v1/models/$MODEL_ID/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Support FAQ dataset"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

### Upload sample dataset

```bash
curl -X POST http://localhost:8000/api/v1/datasets/$DATASET_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -F "upload=@samples/text_to_text.csv;type=text/csv"
```

### Validate dataset

```bash
curl -X POST http://localhost:8000/api/v1/datasets/$DATASET_ID/validate \
  -H "Authorization: Bearer $TOKEN"
```

### Start mock training

```bash
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/models/$MODEL_ID/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\":\"$DATASET_ID\",\"epochs\":1}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
```

### Track training

```bash
curl http://localhost:8000/api/v1/training-jobs/$JOB_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Create API key

```bash
API_KEY=$(curl -s -X POST http://localhost:8000/api/v1/models/$MODEL_ID/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Local dev key"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['api_key'])")
```

### Run inference

```bash
curl -X POST http://localhost:8000/api/v1/inference/$MODEL_ID \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"How do I reset my password?"}'
```

## 6. Dataset formats

### Text-to-Text CSV

```csv
input,output
"How do I reset my password?","Click Forgot Password on the login page and follow the email instructions."
"What is your refund policy?","Refunds are available within 30 days for eligible purchases."
```

### Text-to-Text JSONL

```jsonl
{"input":"How do I reset my password?","output":"Click Forgot Password on the login page and follow the email instructions."}
{"input":"What is your refund policy?","output":"Refunds are available within 30 days for eligible purchases."}
```

### Text-to-Image manifest CSV

```csv
image_path,caption
product_001.png,"A clean studio photo of a red insulated water bottle on a white background."
character_001.jpg,"A fantasy game character with silver armor, a blue cape, and a confident pose."
```

### Text-to-Image manifest JSONL

```jsonl
{"image_path":"product_001.png","caption":"A clean studio photo of a red insulated water bottle on a white background."}
{"image_path":"character_001.jpg","caption":"A fantasy game character with silver armor, a blue cape, and a confident pose."}
```

## 7. Important security notes

- Store passwords as hashes only.
- Store API keys as hashes only. The raw key is returned once during creation.
- Keep `API_SECRET_KEY` and `API_KEY_PEPPER` out of git.
- Do not automatically retrain from feedback. Feedback is stored, reviewed, approved, and only then used by a retraining request.
- Owner-scoped queries prevent one user from reading another user’s models.
- Use private S3 buckets in production. Public MinIO access is only convenient for local development.
- Add rate limiting before public production launch.

## 8. What to replace next

The current training and inference services are intentionally mocked:

- Replace `app/workers/jobs.py` with real Transformers/PEFT and Diffusers/LoRA training.
- Replace `app/services/inference.py` with a real model server or local pipeline.
- Add presigned upload URLs for large files.
- Add virus/malware scanning for uploaded files.
- Add billing and usage limits.
