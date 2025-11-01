import os
import subprocess
import time

import psycopg2
import pytest
import requests

from src.infrastructure.adapter.outbound.email import MailhogEmailSender
from src.infrastructure.config import DatabaseConfig, SmtpConfig


def check_environment():
    """Check if Docker is available and working properly"""
    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            raise Exception("Docker CLI not found or not working")

        result = subprocess.run(
            ["docker", "run", "--rm", "hello-world"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise Exception(f"Docker test failed: {result.stderr}")

        try:
            subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            use_compose = "docker-compose"
        except:
            try:
                subprocess.run(
                    ["docker", "compose", "version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True,
                )
                use_compose = "docker compose"
            except Exception as e:
                raise Exception(
                    f"Neither docker-compose nor docker compose found: {str(e)}"
                )

        print(f"Docker environment is ready (using {use_compose})")
        return use_compose
    except Exception as e:
        pytest.exit(
            f"Docker environment not available: {str(e)}\n"
            "Please ensure Docker Desktop or Rancher Desktop is running properly."
        )


compose_cmd = check_environment()


@pytest.fixture(scope="session")
def docker_compose():
    """Manage test containers using docker-compose with cross-platform compatibility"""
    print("\n> Starting test containers...")

    timestamp = int(time.time())
    compose_file = f"docker-compose-test-{timestamp}.yml"
    container_name = f"test_postgres_{timestamp}"

    compose_content = f"""
version: "3.8"
services:
  postgres:
    image: postgres:13
    container_name: {container_name}
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5431:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d test_db"]
      interval: 1s
      timeout: 5s
      retries: 10
  mailhog:
    image: mailhog/mailhog:latest
    container_name: test_mailhog
    ports:
      - "1024:1025"
      - "8024:8025"
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "1025"]
      interval: 1s
      timeout: 5s
      retries: 10
    """

    with open(compose_file, "w") as f:
        f.write(compose_content)

    try:
        cmd = compose_cmd.split(" ") + ["-f", compose_file, "up", "-d"]
        subprocess.run(cmd, check=True, capture_output=True)

        # Wait for PostgreSQL to be ready
        for i in range(30):
            try:
                conn = psycopg2.connect(
                    dbname="test_db",
                    user="test_user",
                    password="test_password",
                    host="localhost",
                    port=5431,
                    connect_timeout=5,
                )
                conn.close()
                print(f"\n> PostgreSQL ready after {i + 1} attempts")
                break
            except psycopg2.OperationalError as e:
                if i == 29:  # Last attempt
                    log_cmd = compose_cmd.split(" ") + [
                        "-f",
                        compose_file,
                        "logs",
                        "postgres",
                    ]
                    result = subprocess.run(log_cmd, capture_output=True, text=True)
                    pytest.fail(
                        f"Could not connect to PostgreSQL. Error: {str(e)}\nLogs:\n{result.stdout}"
                    )
                time.sleep(1)

        yield compose_file

    finally:
        print("\n> Stopping test containers...")
        down_cmd = compose_cmd.split(" ") + ["-f", compose_file, "down"]
        subprocess.run(down_cmd, check=True, capture_output=True)
        if os.path.exists(compose_file):
            try:
                os.remove(compose_file)
            except:
                print(f"Warning: Could not remove compose file {compose_file}")
        print("> Containers stopped and cleaned up")


@pytest.fixture(scope="session")
def db_config(docker_compose):
    """Database config for test container"""
    return DatabaseConfig(
        database="test_db",
        user="test_user",
        password="test_password",
        host="localhost",
        port=5431,
    )


@pytest.fixture(scope="session")
def initialized_db(db_config):
    """Initialize database tables with better error handling"""
    print(f"> Initializing database tables...")
    conn = None
    try:
        # Add retry logic for database initialization
        for attempt in range(5):
            try:
                conn = psycopg2.connect(
                    dbname=db_config.database,
                    user=db_config.user,
                    password=db_config.password,
                    host=db_config.host,
                    port=5431,
                    connect_timeout=5,
                )
                with conn.cursor() as cur:
                    cur.execute("DROP TABLE IF EXISTS users")
                    cur.execute(
                        """
                        CREATE TABLE users (
                            email VARCHAR(255) PRIMARY KEY,
                            password_hash VARCHAR(255) NOT NULL,
                            is_active BOOLEAN DEFAULT FALSE,
                            activation_code VARCHAR(4),
                            code_expires_at TIMESTAMPTZ
                        )
                    """
                    )
                conn.commit()
                print("> Database initialized successfully")
                return db_config
            except psycopg2.OperationalError as e:
                if attempt == 4:  # Last attempt
                    raise
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
    except Exception as e:
        pytest.fail(f"Failed to initialize database: {str(e)}")
    finally:
        if conn:
            conn.close()


@pytest.fixture(scope="session")
def mailhog_container(docker_compose):
    """Ensure MailHog is running via docker-compose"""
    for i in range(30):
        try:
            response = requests.get("http://localhost:8024/api/v2/messages")
            if response.status_code == 200:
                print(f"MailHog ready after {i + 1} attempts")
                break
        except:
            time.sleep(1)
    else:
        pytest.fail("Could not connect to MailHog")
    requests.delete("http://localhost:8024/api/v1/messages")
    yield


@pytest.fixture(scope="session")
def smtp_config():
    """SMTP configuration for MailHog"""
    return SmtpConfig(
        host="localhost", port=1024, sender_email="noreply@spookymotion.com", timeout=10
    )


@pytest.fixture(scope="session")
def email_sender(smtp_config, mailhog_container):
    """Email sender instance"""
    return MailhogEmailSender(smtp_config)
