from fastapi import APIRouter, HTTPException, status

from app.auth.jwt import create_access_token
from app.auth.users import authenticate
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    user = authenticate(request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    token = create_access_token(user.user_id, user.tenant_id, user.tenant_name)
    return LoginResponse(token=token)
