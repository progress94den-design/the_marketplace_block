from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.user import User
from src.app.schemas.user import UserCreate, ShowUser
from src.app.brokers.producer import send_registration_email


class UserService:
    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> ShowUser:
        new_user = User(
            email=data.email,
            # hashed_password=hashed_pwd,
            hashed_password=data.password,
            phone_number=data.phone_number,
            name=data.name
        )

        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)

        await send_registration_email(
            email=new_user.email,
            name=new_user.name
        )

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
