from src.domain.model import User
from src.domain.model import Email
from src.domain.port import UserRepositoryPort
from src.domain.exception import UserNotFoundException


class ActivateUserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def activate_user(self, email: str, activation_code: str) -> User:
        user = self.user_repository.find_by_email(Email(email))
        if user is None:
            raise UserNotFoundException(f"No user found with email: {email}")

        user.activate(activation_code)
        self.user_repository.save(user)
        return user
