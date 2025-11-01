from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for the database connection"""

    host: str = "postgres"
    database: str = "user_registration"
    user: str = "postgres"
    password: str = "password"
    port: int = 5432
