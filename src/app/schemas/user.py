import re
import uuid
from pydantic import BaseModel, EmailStr, field_validator

PHONE_PATTERN = re.compile(r"^\+7\(\d{3}\)\d{7}$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    email: EmailStr
    phone_number: str
    name: str
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    name: str

    @field_validator("phone_number")
    def validate_phone_number(cls, values):
        if not re.match(PHONE_PATTERN, values):
            raise ValueError("Invalid phone number. The phone number must be in the format +7(999)1234567")
        return values


class UserLogin(BaseModel):
    email: EmailStr
    password: str
