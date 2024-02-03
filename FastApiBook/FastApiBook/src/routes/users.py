from cloudinary import CloudinaryImage, uploader, config
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi_users import BaseUserManager, models
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config as cfg
from src.database.fu_db import get_db
from src.models.models import User
from src.repository.users import update_avatar_url
from src.schemas.user import UserRead, UserUpdate
from src.services.auth import fastapi_users, current_active_user, get_user_manager

router = APIRouter()

config(
    cloud_name=cfg.CLD_NAME,
    api_key=cfg.CLD_API_KEY,
    api_secret=cfg.CLD_API_SECRET,
    secure=True,
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)


@router.patch("/avatar", response_model=UserRead, dependencies=[Depends(RateLimiter(times=1, seconds=20))],
              tags=["users"])
async def update_avatar(
        file: UploadFile = File(),
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_db),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    """
    Update the avatar of a user.

    :param file: The file containing the new avatar image.
    :type file: UploadFile
    :param user: The user for whom the avatar is being updated.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :param user_manager: The user manager.
    :type user_manager: BaseUserManager[models.UP, models.ID]

    :return: The updated user object.
    :rtype: UserRead

    :dependencies:
        - RateLimiter: A rate limiter dependency that limits the number of requests.
        - current_active_user: A dependency function that retrieves the current active user.
        - get_db: A dependency function that retrieves the database session.
        - get_user_manager: A dependency function that retrieves the user manager.
    """
    public_id = f"AddressBook/{user.email}/{file.filename}"
    res = uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    updated_user = await update_avatar_url(user, res_url, db)
    await user_manager.on_after_update(user, updated_user)
    return updated_user
