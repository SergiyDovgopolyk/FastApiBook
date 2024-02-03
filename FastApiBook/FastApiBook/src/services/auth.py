import uuid

from typing import Optional, Dict, Any
from fastapi import Depends, Request, BackgroundTasks
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserAlreadyExists
from libgravatar import Gravatar
from pickle import dumps, loads
from redis.asyncio import Redis
from starlette.responses import Response

from src.conf.config import config
from src.database.fu_db import User, get_user_db
from src.services.email import send_email_verification, send_email_forgot_password


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    User manager class responsible for managing user operations.

    :param user_db: The user database.
    :type user_db: SQLAlchemyUserDatabase
    :param background_tasks: The background tasks.
    :type background_tasks: BackgroundTasks
    """
    reset_password_token_secret = config.SECRET_KEY_JWT
    verification_token_secret = config.SECRET_KEY_JWT
    cache = Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def __init__(self, user_db: SQLAlchemyUserDatabase, background_tasks: BackgroundTasks):
        super().__init__(user_db)
        self.background_tasks = background_tasks

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Triggered after a user is registered.

        :param user: The registered user.
        :type user: User
        :param request: The request associated with the registration.
        :type request: Optional[Request]
        """
        await self.request_verify(user, request)

    async def create(self, user_create: schemas.UC, safe: bool = False, request: Optional[Request] = None) -> models.UP:
        """
        Create a new user.

        :param user_create: The user creation data.
        :type user_create: schemas.UC
        :param safe: Flag indicating whether to create a safe user or not. Defaults to False.
        :type safe: bool, optional
        :param request: The request object. Defaults to None.
        :type request: Optional[Request], optional

        :return: The created user.
        :rtype: models.UP

        :raises UserAlreadyExists: If a user with the same email already exists.
        """
        await self.validate_password(user_create.password, user_create)
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise UserAlreadyExists()

        user_dict = (user_create.create_update_dict() if safe else user_create.create_update_dict_superuser())
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        avatar = None
        try:
            g = Gravatar(user_create.email)
            avatar = g.get_image()
        except Exception as err:
            print(err)
        user_dict["avatar"] = avatar

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        """
        Asynchronously handles the logic after a user has successfully logged in.

        :param user: An instance of the UP model representing the logged-in user.
        :type user: models.UP
        :param request: An optional instance of the Request class representing the HTTP request.
        :type request: Optional[Request]
        :param response: An optional instance of the Response class representing the HTTP response.
        :type response: Optional[Response]

        :return: The cached user data retrieved from the cache.
        :rtype: Any
        """
        user_hash = str(user.email)
        cached_user = await self.cache.get(user_hash)

        if cached_user is None:
            cached_user = await self.get_by_email(user.email)
            await self.cache.set(user_hash, dumps(cached_user))
            await self.cache.expire(user_hash, 300)
        else:
            cached_user = loads(cached_user)
        return cached_user

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        """
        Asynchronously verifies a request after it has been processed,
        by sending an email verification link to the user.

        :param user: The user object.
        :type user: User
        :param token: The verification token.
        :type token: str
        :param request: The request object, defaults to None.
        :type request: Optional[Request], optional
        """
        host = str(request.base_url)
        self.background_tasks.add_task(send_email_verification, user.email, user.username, token, host)

    async def on_after_verify(self, user: models.UP, request: Optional[Request] = None) -> None:
        """
        A function that is called after a user has been verified.

        :param user: The user object that has been verified.
        :type user: models.UP
        :param request: An optional request object.
        :type request: Optional[Request]
        """
        print('verified user', user.email)

    async def on_after_update(
        self,
        user: models.UP,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        """
        A function that is called after an update is made.

        :param user: The user object.
        :type user: models.UP
        :param update_dict: A dictionary containing the update information.
        :type update_dict: Dict[str, Any]
        :param request: An optional request object.
        :type request: Optional[Request]
        """
        await self.on_after_login(user)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """
        Handle the event that occurs after a user has requested to reset their password.

        :param user: The user who requested the password reset.
        :type user: User
        :param token: The password reset token.
        :type token: str
        :param request: The HTTP request associated with the password reset, defaults to None.
        :type request: Optional[Request], optional
        """
        host = str(request.base_url)
        self.background_tasks.add_task(send_email_forgot_password, user.email, user.username, token, host)


async def get_user_manager(background_tasks: BackgroundTasks = None,
                           user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    An asynchronous function that returns a user manager.

    :param background_tasks: The background tasks.
    :type background_tasks: BackgroundTasks
    :param user_db: The user database. Defaults to the result of `get_user_db`.
    :type user_db: SQLAlchemyUserDatabase, optional

    :return: The user manager.
    :rtype: UserManager
    """
    yield UserManager(user_db, background_tasks)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """
   Get the JWT strategy.

   :return: An instance of JWTStrategy.
   :rtype: JWTStrategy
   """
    return JWTStrategy(secret=config.SECRET_KEY_JWT, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
