from fastapi import FastAPI
from backend.routers.crew_member import router as crew_member_router

app = FastAPI(title='Crew Management API')

app.include_router(crew_member_router)
