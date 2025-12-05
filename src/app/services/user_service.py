from passlib.context import CryptContext
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.user import User
from src.app.schemas.user import UserCreate, ShowUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


class UserService:
    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> ShowUser:
        # hashed_pwd = hash_password(data.password)

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
        # return new_user
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
