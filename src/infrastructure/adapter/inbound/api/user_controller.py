from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic

from src.application.dto.request import ActivateUserRequest, RegisterUserRequest
from src.application.dto.response import UserResponse
from src.application.service import ActivateUserService, RegisterUserService
from src.infrastructure.dependencies import (
    get_activate_service,
    get_register_service,
    verify_credentials,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])
app = FastAPI()
security = HTTPBasic()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(
    request: RegisterUserRequest,
    service: RegisterUserService = Depends(get_register_service),
) -> UserResponse:
    try:
        user = service.register_user(request.email, request.password)
        return UserResponse.from_domain(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/activate", response_model=UserResponse, status_code=status.HTTP_200_OK)
def activate_user(
    request: ActivateUserRequest,
    service: ActivateUserService = Depends(get_activate_service),
    email: str = Depends(verify_credentials),
) -> UserResponse:
    try:
        user = service.activate_user(email, request.activation_code)
        return UserResponse.from_domain(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


app.include_router(router)
