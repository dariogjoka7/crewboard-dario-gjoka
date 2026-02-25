from fastapi.security import HTTPAuthorizationCredentials

from backend.auth.models.login_request import LoginRequest
from backend.auth.models.token_response import TokenResponse
from backend.auth.security import verify_password, create_access_token
from backend.auth.user_repo import UserRepo
from backend.auth.security import decode_access_token
from backend.db.models.user import User
from backend.exceptions.custom_exceptions import UnauthorizedException


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials | None) -> User:
        if not credentials:
            raise UnauthorizedException('Bearer token is missing from headers')

        token = credentials.credentials
        payload = decode_access_token(token)

        if payload is None:
            raise UnauthorizedException('Invalid or expired token')

        email: str = payload.get("sub")
        if email is None:
            raise UnauthorizedException('Invalid token payload')

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UnauthorizedException('User no longer exists')

        return user

    async def login_user(self, body: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(body.email)

        if not user or not verify_password(body.password, user.password):
            raise UnauthorizedException('Invalid email or password')

        token = create_access_token(data={"sub": user.email})

        return TokenResponse(access_token=token)
