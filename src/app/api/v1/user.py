from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.user import UserCreate, ShowUser
from src.app.services.user_service import UserService
from src.app.db.session import get_async_session


user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(user_data: UserCreate, db_session: AsyncSession = Depends(get_async_session)):
    return await UserService.create_user(data=user_data, db_session=db_session)


@user_router.get("/", response_model=list[ShowUser])
async def get_users(db_session: AsyncSession = Depends(get_async_session)):
    return await UserService.get_all_users(db_session=db_session)
