from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from fastapi_users import BaseUserManager, models, schemas, exceptions
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from src.database.fu_db import get_db
from src.schemas.user import UserCreate, UserRead
from src.services.auth import auth_backend, fastapi_users, get_user_manager

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


@router.get(
    "/auth/confirmed_email/{token}",
    response_model=UserRead,
    name="verify:verify",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.VERIFY_USER_BAD_TOKEN: {
                            "summary": "Bad token, not existing user or"
                                       "not the e-mail currently set for the user.",
                            "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                        },
                        ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                            "summary": "The user is already verified.",
                            "value": {
                                "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                            },
                        },
                    }
                }
            },
        }
    },
    tags=["auth"]
)
async def confirmed_email(
        token: str,
        request: Request,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)
):
    """
    Verify a user's email address using a confirmation token.

    :param token: The confirmation token.
    :type token: str
    :param request: The HTTP request object.
    :type request: Request
    :param user_manager: The user manager.
    :type user_manager: BaseUserManager[models.UP, models.ID]

    :return: The user object after verification.
    :rtype: UserRead

    :raises HTTPException: If the confirmation token is invalid or the user does not exist.
                           If the user is already verified.
    """
    try:
        user = await user_manager.verify(token, request)
        return schemas.model_validate(UserRead, user)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )


@router.get('/{username}')
async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the email of the specified user from the database and returns it as a file response.

    :param username: The username of the user whose email is being requested.
    :type username: str
    :param response: The response object used to send the file response.
    :type response: Response
    :param db: The asynchronous database session. Defaults to the session obtained from the `get_db` dependency.
    :type db: AsyncSession, optional

    :return: The file response containing the requested email as a PNG image.
    :rtype: FileResponse
    """

    print('--------------------')
    print(f'{username} відкрив email')
    print('--------------------')
    return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")
