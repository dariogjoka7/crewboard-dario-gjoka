from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from backend.exceptions.exception_handlers import register_exception_handling
from backend.routers.assignment import router as assignment_router
from backend.routers.crew_member import router as crew_member_router
from backend.routers.flight import router as flight_router
from backend.auth.router import router as auth_router

app = FastAPI()

origins = [
    "http://localhost:5173",  # your React dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Crew Management API",
        version="1.0.0",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply security globally to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(auth_router)
app.include_router(crew_member_router)
app.include_router(flight_router)
app.include_router(assignment_router)

register_exception_handling(app)
