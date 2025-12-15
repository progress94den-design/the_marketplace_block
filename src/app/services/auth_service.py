from fastapi import HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.app.db.models.user import User
from src.app.schemas.user import UserLogin, ShowUser
from src.app.core.jwt import create_access_token


class AuthService:
    @staticmethod
    async def get_user_by_email(email: EmailStr, db_session: AsyncSession) -> User | None:
        result = await db_session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def login(data: UserLogin, db_session: AsyncSession, response: Response):
        user = await AuthService.get_user_by_email(data.email, db_session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password",
            )

        # if not Hasher.verify_password(data.password, user.hashed_password):
        if data.password != user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password",
            )

        access_token = create_access_token(
            data={"sub": str(user.user_id)}
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # True в prod
            samesite="lax",
        )

        return ShowUser(
            user_id=user.user_id,
            email=user.email,
            phone_number=user.phone_number,
            name=user.name,
            is_active=user.is_active,
        )

    @staticmethod
    async def logout(response: Response):
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=False,  # True в prod
            samesite="lax",
        )
        return {"message": "Logged out"}
