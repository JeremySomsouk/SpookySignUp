import psycopg2
import uuid
from psycopg2.extras import DictCursor

from src.domain.model import User, Email, ActivationCode
from src.domain.port.user_repository_port import UserRepositoryPort
from src.infrastructure.config.database_config import DatabaseConfig


class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config

    def _get_connection(self):
        """Lazy connection initialization"""
        return psycopg2.connect(
            dbname=self.db_config.database,
            user=self.db_config.user,
            password=self.db_config.password,
            host=self.db_config.host,
            port=self.db_config.port,
        )

    def save(self, user: User) -> None:
        query = """
        INSERT INTO users (id, email, password_hash, is_active, activation_code, code_expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
            password_hash = EXCLUDED.password_hash,
            is_active = EXCLUDED.is_active,
            activation_code = EXCLUDED.activation_code,
            code_expires_at = EXCLUDED.code_expires_at
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        str(user.id),
                        user.email.value,
                        user.password_hash,
                        user.is_active,
                        user.activation_code.value if user.activation_code else None,
                        (
                            user.activation_code.expires_at
                            if user.activation_code
                            else None
                        ),
                    ),
                )
            conn.commit()

    def find_by_id(self, user_id: uuid.UUID) -> User | None:
        query = "SELECT * FROM users WHERE id = %s"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, (user_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return User(
                    id=row["id"],
                    email=Email(row["email"]),
                    password_hash=row["password_hash"],
                    is_active=row["is_active"],
                    activation_code=ActivationCode(
                        row["activation_code"], row["code_expires_at"]
                    ),
                )

    def find_by_email(self, email: Email) -> User | None:
        query = "SELECT * FROM users WHERE email = %s"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, (email.value,))
                row = cur.fetchone()
                if not row:
                    return None
                return User(
                    id=row["id"],
                    email=Email(row["email"]),
                    password_hash=row["password_hash"],
                    is_active=row["is_active"],
                    activation_code=ActivationCode(
                        row["activation_code"], row["code_expires_at"]
                    ),
                )
