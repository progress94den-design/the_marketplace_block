from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.user import UserLogin, ShowUser
from src.app.services.auth_service import AuthService
from src.app.db.models.user import User
from src.app.db.session import get_async_session
from src.app.core.jwt import get_current_user

auth_router = APIRouter()


@auth_router.post("/", response_model=ShowUser)
async def login(data: UserLogin, response: Response, db_session: AsyncSession = Depends(get_async_session)):
    return await AuthService.login(data, db_session, response)


@auth_router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    return await AuthService.logout(response)
