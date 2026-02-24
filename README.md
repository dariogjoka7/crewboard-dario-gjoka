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

## Database
- Postgres 16
- Data persisted in `pgdata` volume


## Troubleshooting
- Ensure `.env` files are set up for backend and frontend if needed.
- Check ports and volumes in `docker-compose.yml`.