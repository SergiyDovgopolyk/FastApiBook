from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User


async def update_avatar_url(user: User, url: str | None, db: AsyncSession):
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
