
# Signup - Clean Architecture Application with FastAPI and Docker
[![CI](https://github.com/JeremySomsouk/SpookySignUp/actions/workflows/ci.yml/badge.svg)](https://github.com/JeremySomsouk/SpookySignUp/actions/workflows/ci.yml)

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)


## Project Overview

A modern application built with Clean Architecture, Domain-Driven Design, and FastAPI, featuring:
- Hexagonal architecture with clear separation of concerns
- Docker containerization
- PostgreSQL database integration
- Email service integration: Local but easily replaceable
- Comprehensive testing strategy

---

## Architecture
### High-Level Component Diagram
```mermaid
%%{init: {'theme': 'neutral'}}%%
graph TD
    %% Clients
    subgraph Clients
        A[Web Clients] -->|HTTP| B[FastAPI]
        D[Other Services] -->|API| B
    end

    %% Application
    subgraph Application
        B -->|uses| E[SignupUserApplication]
        E -->|orchestrates| F[Domain Layer]
        E -->|uses| G[Outbound Ports]
    end

    %% Domain
    subgraph Domain
        F -->|contains| H[User]
        F -->|contains| I[ActivationCode]
        F -->|contains| Z[Email]
        F -->|defines| G
    end

    %% Infrastructure
    subgraph Infrastructure
        G -->|implemented by| J[PostgreSQL Repository]
        G -->|implemented by| K[Email Service]
    end

    %% External Systems
    subgraph External Systems
        J -->|stores| M[(PostgreSQL)]
        K -->|sends| N[SMTP Server]
    end

    %% Containerization
    subgraph Containerization
        O[Docker] -->|contains| B
        O -->|contains| J
        O -->|contains| K
        O -->|contains| P[Nginx]
    end

    %% Styling
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style E fill:#bbf,stroke:#333
    style F fill:#9f9,stroke:#333
    style J fill:#f99,stroke:#333
    style K fill:#f99,stroke:#333
    style O fill:#99f,stroke:#333
```

### Hexagonal architecture
```mermaid
%%{init: {'theme': 'forest'}}%%
graph LR
    subgraph Inbound
        API[HTTP API]
    end

    subgraph Application
        Services[Application Services]
        DTOs[Data Transfer Objects]
    end

    subgraph Domain
        Entities[User Model]
        Values[Email / ActivationCode Values]
        Ports[Interface Ports]
    end

    subgraph Outbound
        DB[Database Adapter]
        Email[Email Service Adapter]
    end

    API --> DTOs
    DTOs --> Services

    Services --> Entities
    Services --> Values

    Services --> Ports

    Ports --> DB
    Ports --> Email

    classDef inbound fill:#f9f,stroke:#333
    classDef app fill:#bbf,stroke:#333
    classDef domain fill:#9f9,stroke:#333
    classDef outbound fill:#f99,stroke:#333

    class API inbound
    class Services,DTOs app
    class Entities,Values,DomainServices,Ports domain
    class DB,Email outbound
```

---

# How to run this application
```bash
docker-compose up --build
```

## Test the API
1) Register a user
```bash
curl -X POST http://localhost:8080/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "account@spookymotion.com", "password": "mypassword123"}'
```

2) Retrieve the email sent here: http://localhost:8025/
3) Activate the account 
```bash
curl -X POST http://localhost:8080/api/v1/users/activate \
  -u "account@spookymotion.com:mypassword123" \
  -H "Content-Type: application/json" \
  -d '{"activation_code": "{{ the retrieved activation code }}"}'
```

# How to launch the automated tests
## For unit tests ran from the container
```bash
docker-compose up --build
```
```bash
docker-compose exec app pytest tests/unit/
```

## For all tests from local using testcontainers
Only if pytest installed locally, and docker compose not up
```bash
pytest
```

# API Documentation
The API is self-documenting with:

Swagger UI: http://localhost:8080/docs

## User Registration Endpoints
   Endpoint | Method | Description | Request Body | Response                          | Status Codes | Authentication |
 |----------|--------|-------------|--------------|-----------------------------------|--------------|----------------|
 | `/api/v1/users/register` | POST | Register a new user | `RegisterUserRequest` (email, password) | `UserResponse` (email, is_active) | 201: Created, 400: Bad Request, 422: Validation Error | None |
 | `/api/v1/users/activate` | POST | Activate a user account | `ActivateUserRequest` (activation_code) | `UserResponse`  (email, is_active)                   | 200: OK, 400: Bad Request, 401: Unauthorized, 422: Validation Error | Basic Auth |

## Example queries
Registration
```bash
curl -X POST http://localhost:8080/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "account@spookymotion.com", "password": "mypassword123"}'
```

Activation
```bash
curl -X POST http://localhost:8080/api/v1/users/activate \
  -u "account@spookymotion.com:mypassword123" \
  -H "Content-Type: application/json" \
  -d '{"activation_code": "9494"}'
```

