from pathlib import Path
from enum import Enum

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from src.schemas.mail import ActivationMail
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
    ACTIVATION = "activation-mail.html"


class MailService:

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

    def send_activation_mail(
        self,
        background_tasks: BackgroundTasks,
        body: ActivationMail,
    ):
        self.send_mail(
            background_tasks=background_tasks,
            subject="Activate your account",
            recipients=[body.email],
            template_body={**body.model_dump()},
            template_name=MailTemplates.ACTIVATION,
        )
