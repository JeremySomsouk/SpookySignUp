from fastapi import FastAPI

from src.infrastructure.adapter.inbound import api_router

app = FastAPI(
    title="Spooky User Sign Up API",
    description="API to register and activate a user.",
    version="1.0.0",
)

app.include_router(api_router)
