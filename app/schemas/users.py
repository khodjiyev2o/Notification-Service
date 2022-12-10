
from pydantic import BaseModel, validator, Field, EmailStr
from typing import Optional

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    email: EmailStr
    phone_number: int = Field(gt=0,le=999999999)
    operator_code: int = Field(gt=0,le=999)
    time_zone: Optional[str] = Field(min_length=1, max_length=4096)
    password1: str = Field(min_length=8, max_length=32)
    password2: str = Field(min_length=8, max_length=32)
    

    @validator('password2')
    def passwords_match(cls, password2, values):
        if 'password1' in values and password2 != values['password1']:
            raise ValueError('passwords do not match')
        return password2

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: int = Field(gt=0)
    username: str = Field(min_length=1, max_length=32)
    email: EmailStr
    phone_number: int = Field(gt=0,le=999999999)
    operator_code: int = Field(gt=0,le=999)
    time_zone: Optional[str] = Field(min_length=1, max_length=4096)
    admin : Optional[bool] = Field(default=False)


class UserAlterSchema(BaseModel):
    username: Optional[str] = Field(min_length=1, max_length=32)
    phone_number: int = Field(gt=0,le=999999999)
    operator_code: int = Field(gt=0,le=999)
    time_zone: Optional[str] = Field(min_length=1, max_length=4096)
    password: Optional[str] = Field(min_length=8, max_length=32)



class UserAdminShema(BaseModel):
    username: str = Field(min_length=1, max_length=32,default='khodjiyev2o')
    email: EmailStr = Field(default='admin@gmail.com')
    phone_number: int = Field(gt=0,le=999999999, default='913665113')
    operator_code: int = Field(gt=0, le=999, default='998')
    time_zone: Optional[str] = Field(min_length=1, max_length=4096, default="CET")
    password1: str = Field(min_length=8, max_length=32, default='692249735')
    password2: str = Field(min_length=8, max_length=32, default='692249735')
    admin: bool = Field(default=True)

    @validator('password2')
    def passwords_match(cls, password2, values):
        if 'password1' in values and password2 != values['password1']:
            raise ValueError('passwords do not match')
        return password2

    class Config:
        orm_mode = True