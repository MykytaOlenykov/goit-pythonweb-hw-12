from pathlib import Path
from enum import Enum

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from src.schemas.mail import VerificationMail, ResetPasswordMail
from src.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


class MailTemplates(str, Enum):
    """
    Enum for different mail templates.

    Attributes:
        - VERIFICATION: Template used for verification emails.
    """

    VERIFICATION = "verification-mail.html"
    RESET_PASSWORD = "reset-password.html"


class MailService:
    """
    MailService handles sending emails.

    Args:
        - config: ConnectionConfig - Configuration object for sending emails.

    Methods:
        - send_mail: Sends an email using FastMail.
        - send_verification_mail: Sends a verification email to the user.
    """

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.fm = FastMail(config)

    def send_mail(
        self,
        background_tasks: BackgroundTasks,
        subject: str,
        recipients: list[str],
        template_body: dict,
        template_name: MailTemplates,
    ):
        """
        Sends an email using FastMail.

        Args:
            - background_tasks: BackgroundTasks - Background task to handle sending.
            - subject: str - The subject of the email.
            - recipients: list[str] - List of recipients.
            - template_body: dict - The content of the email template.
            - template_name: MailTemplates - The template used to generate the email.

        """

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_body,
            subtype=MessageType.html,
        )
        background_tasks.add_task(
            self.fm.send_message,
            message,
            template_name=template_name.value,
        )

    def send_verification_mail(
        self,
        background_tasks: BackgroundTasks,
        body: VerificationMail,
    ):
        """
        Sends a verification email to the user.

        Args:
            - background_tasks: BackgroundTasks - Background task to handle sending.
            - body: VerificationMail - The data to populate the email template.

        """

        self.send_mail(
            background_tasks=background_tasks,
            subject="Activate your account",
            recipients=[body.email],
            template_body={**body.model_dump()},
            template_name=MailTemplates.VERIFICATION,
        )

    def send_reset_password_mail(
        self,
        background_tasks: BackgroundTasks,
        body: ResetPasswordMail,
    ):
        """
        Sends a reset password email.

        Args:
            background_tasks: BackgroundTasks - The background tasks for sending the email asynchronously.
            body: ResetPasswordMail - The body of the reset password email containing the recipient's email and other necessary details.

        Sends an email with a reset password link to the provided email address.
        """

        self.send_mail(
            background_tasks=background_tasks,
            subject="Reset password",
            recipients=[body.email],
            template_body={**body.model_dump()},
            template_name=MailTemplates.RESET_PASSWORD,
        )
