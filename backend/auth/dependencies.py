from typing import Annotated
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.user_repo import UserRepo
from backend.dependencies import get_session_dep
from backend.auth.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service(session: Annotated[AsyncSession, Depends(get_session_dep)]) -> UserService:
    user_repo = UserRepo(session)

    return UserService(user_repo)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: Annotated[UserService, Depends(get_user_service)]
):
    return await service.get_current_user(credentials)
