from passlib.context import CryptContext

from src.domain.exception import EmailAlreadyExistsException
from src.domain.model import User, Email, ActivationCode
from src.domain.port import EmailSenderPort, UserRepositoryPort


class RegisterUserService:
    def __init__(
        self, user_repository: UserRepositoryPort, email_sender: EmailSenderPort
    ):
        self.user_repository = user_repository
        self.email_sender = email_sender
        self.crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, email: str, plain_password: str) -> User:
        """Registers a new user and sends an activation email"""
        user_email = Email(email)
        existing_user = self.user_repository.find_by_email(user_email)
        if existing_user is not None:
            raise EmailAlreadyExistsException(f"Email {email} already registered.")
        password_hash = self.crypt_context.hash(plain_password)
        activation_code = ActivationCode.generate_activation_code()
        user = User(
            email=user_email,
            password_hash=password_hash,
            activation_code=activation_code,
        )
        self.user_repository.save(user)
        self.email_sender.send_activation_email(user_email, activation_code.value)
        return user
