import uuid

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Path
from fastapi.security import HTTPBasic

from src.application.dto.request import ActivateUserRequest, RegisterUserRequest
from src.application.dto.response import UserResponse
from src.application.service import ActivateUserService, RegisterUserService
from src.domain.model import User
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


@router.post(
    "/{user_id}/activate", response_model=UserResponse, status_code=status.HTTP_200_OK
)
def activate_user(
    user_id: uuid.UUID = Path(...),
    request: ActivateUserRequest = ...,
    service: ActivateUserService = Depends(get_activate_service),
    logged_user: User = Depends(verify_credentials),
) -> UserResponse:
    if str(user_id) != str(logged_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only activate your own account.",
        )

    try:
        user = service.activate_user(logged_user.id, request.activation_code)
        return UserResponse.from_domain(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


app.include_router(router)
