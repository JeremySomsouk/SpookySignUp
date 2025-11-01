from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from src.application.service import RegisterUserService, ActivateUserService
from src.domain.model import Email
from src.infrastructure.adapter.outbound import (
    PostgresUserRepository,
    MailhogEmailSender,
)
from src.infrastructure.config import DatabaseConfig, SmtpConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_repository():
    return PostgresUserRepository(DatabaseConfig())


def get_email_sender():
    return MailhogEmailSender(SmtpConfig())


def get_register_service(
    user_repository=Depends(get_user_repository), email_sender=Depends(get_email_sender)
) -> RegisterUserService:
    return RegisterUserService(
        user_repository=user_repository, email_sender=email_sender
    )


def get_activate_service(
    user_repository=Depends(get_user_repository),
) -> ActivateUserService:
    return ActivateUserService(user_repository=user_repository)


def verify_credentials(
    credentials: HTTPBasicCredentials = Security(HTTPBasic()),
    user_repository: PostgresUserRepository = Depends(get_user_repository),
) -> str:
    user = user_repository.find_by_email(Email(credentials.username))
    if not user or not pwd_context.verify(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
