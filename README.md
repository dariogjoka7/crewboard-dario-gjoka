# crewboard-dario-gjoka

# Docker Setup

## Quick Start

1. Build and start all services:

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Postgres: localhost:5432 (user/password/db: crewboard)

## Backend
- FastAPI, SQLAlchemy, Alembic
- Edit `backend/Dockerfile` for custom commands

## Frontend
- Vite, React, TypeScript
- Run the below commands to start the frontend
```bash
npm i
npm run dev
```

## Configure virtual environment
- Run the below commands to create a virtual env locally
```bash
python -m venv
venv/Scripts/Activate.ps1
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Unit tests
- Pytest
- Run the below command in the root folder to run unit tests
```bash
pytest -q
```

## Database
- Postgres 16
- Data persisted in `pgdata` volume


## Troubleshooting
- Ensure `.env` files are set up for backend and frontend if needed.
- Check ports and volumes in `docker-compose.yml`.