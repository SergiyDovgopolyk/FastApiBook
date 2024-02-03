from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import config


conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Sergiy",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email_verification(email: EmailStr, username: str, token: str, host: str):
    """
    Sends an email verification to the specified email address.

    :param email: The email address to send the verification to.
    :type email: EmailStr
    :param username: The username associated with the email address.
    :type username: str
    :param token: The verification token.
    :type token: str
    :param host: The host URL.
    :type host: str

    :raises ConnectionErrors: If there is an error connecting to the email server.
    """
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_email_forgot_password(email: EmailStr, username: str, token: str, host: str):
    """
    Send a forgot password email to the specified email address.

    :param email: The email address of the user.
    :type email: EmailStr
    :param username: The username of the user.
    :type username: str
    :param token: The token for password reset.
    :type token: str
    :param host: The host URL for the application.
    :type host: str
    """
    try:
        message = MessageSchema(
            subject="Forgot password",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="forgot_password.html")
    except ConnectionErrors as err:
        print(err)
