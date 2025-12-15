from pydantic import EmailStr
from sqlalchemy import select
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.user import User
from src.app.schemas.user import UserCreate, ShowUser


class UserService:
    @staticmethod
    async def get_user_by_email(email: EmailStr, db_session: AsyncSession) -> User | None:
        result = await db_session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_phone(phone_number: str, db_session: AsyncSession) -> User | None:
        result = await db_session.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> ShowUser:
        existing_by_email = await UserService.get_user_by_email(data.email, db_session)
        if existing_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        existing_by_phone = await UserService.get_user_by_phone(data.phone_number, db_session)
        if existing_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists",
            )

        new_user = User(
            email=data.email,
            # hashed_password=Hasher.get_password_hash(data.password),
            hashed_password=data.password,
            phone_number=data.phone_number,
            name=data.name
        )

        db_session.add(new_user)
        await db_session.commit()

        # await send_registration_email(
        #     email=new_user.email,
        #     name=new_user.name
        # )

        return ShowUser(
            user_id=new_user.user_id,
            email=new_user.email,
            phone_number=new_user.phone_number,
            name=new_user.name,
            is_active=new_user.is_active,
        )

    @staticmethod
    async def get_all_users(db_session: AsyncSession):
        result = await db_session.execute(select(User))
        return result.scalars().all()
