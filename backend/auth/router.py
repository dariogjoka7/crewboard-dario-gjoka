from typing import Annotated
from fastapi import APIRouter, Depends

from backend.auth.models.login_request import LoginRequest
from backend.auth.models.token_response import TokenResponse

from backend.auth.user_service import UserService
from backend.auth.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    user_service: Annotated[UserService, Depends(get_user_service)],
    body: LoginRequest,
):
    return await user_service.login_user(body)
