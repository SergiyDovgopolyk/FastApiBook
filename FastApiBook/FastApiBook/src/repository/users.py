from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User


async def update_avatar_url(user: User, url: str | None, db: AsyncSession):
    """
    Update the avatar URL for a user.

    :param user: The user object to update.
    :type user: User
    :param url: The new avatar URL. If None, the user's avatar will be removed.
    :type url: str or None
    :param db: The database session.
    :type db: AsyncSession

    :return: The updated user object.
    :rtype: User
    """
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
