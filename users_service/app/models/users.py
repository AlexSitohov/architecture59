from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5)


class UserConfirm(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
