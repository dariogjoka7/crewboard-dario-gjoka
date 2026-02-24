from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models.user import User

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User

    async def get_by_email(self, email: str) -> 'User':
        result = await self.session.execute(select(self.model).where(self.model.email == email))

        return result.scalars().first()
