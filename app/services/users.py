from app.models.users import User
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi import HTTPException, Header, Depends
from app.schemas.users import UserAlterSchema, UserCreateSchema, UserLoginSchema, UserSchema, UserAdminShema
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.ext.asyncio import AsyncSession, async_object_session
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_pagination import Params
from app.db import get_session
from os import getenv
from typing import Optional
from app.services.auth import AuthHandler


auth_cls = AuthHandler()


class UserCRUD:
    def __init__(self, session: Optional[AsyncSession] = None, user: Optional[User] = None):
        if not session:
            self.session = async_object_session(user)
        else:
            self.session = session
        self.user = user

    async def create_user(self, user: UserCreateSchema) -> UserSchema:
        db_user = await self.session.execute(select(User).filter(or_(User.email == user.email, User.username == user.username)))
        db_user = db_user.scalars().first()
        if db_user:
            raise HTTPException(404, 'username or email already in use')
        else:
            new_user = User(username=user.username,
                email=user.email,
                password=sha256.hash(user.password1),
                phone_number=user.phone_number,
                operator_code=user.operator_code,
                time_zone=user.time_zone)
            self.session.add(new_user)
            await self.session.commit()
            return UserSchema(id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                phone_number=new_user.phone_number,
                operator_code=new_user.operator_code,
                time_zone=new_user.time_zone)



    async def login_user(self, user: UserLoginSchema) -> str:
        db_user = await self.session.execute(select(User).filter_by(email=user.email))
        db_user = db_user.scalars().first()
        if db_user:
            if sha256.verify(user.password, db_user.password):
                return auth_cls.encode_token(user.email)
            else:
                raise HTTPException(404, 'user not found')
        else:
            raise HTTPException(404, 'user not found')


    async def patch_user(self, user: UserAlterSchema) -> UserSchema:
        if user.username:
            self.user.username = user.username
        if user.time_zone:
            self.user.time_zone = user.time_zone
        if user.password:
            self.user.password = sha256.hash(user.password)
        if user.operator_code:
            self.user.operator_code = user.operator_code
        if user.phone_number:
            self.user.phone_number = user.phone_number
        await self.session.commit()
        return UserSchema(id=self.user.id,
            username=self.user.username,
            email=self.user.email, 
            phone_number=self.user.phone_number,
            operator_code=self.user.operator_code,
            time_zone=self.user.time_zone)


    async def get_users(self, page: int) -> list[UserSchema]:
        params = Params(page=page, size=10)
        users = await paginate(self.session, select(User), params=params)
        return [UserSchema(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number,operator_code=user.operator_code,time_zone=user.time_zone,admin=user.admin) for user in users.items]



    async def get_user(self, id: int) -> UserSchema:
        user = await self.session.get(User, id)
        if user:
            return UserSchema(id=user.id,
                username=user.username,
                email=user.email, 
                phone_number=user.phone_number,
                operator_code=user.operator_code,
                time_zone=user.time_zone,
                admin=user.admin)
        raise HTTPException(404, 'user not found')


    async def delete_user(self,id: int) -> HTTPException:
        user_tobe_deleted = await self.session.get(User, id)
        if user_tobe_deleted:
            await self.session.delete(user_tobe_deleted)
            await self.session.commit()
            return HTTPException(200,detail=f"User with id {user_tobe_deleted.id} is successfully deleted")
        raise HTTPException(404,f"User with id {id} not found")


    async def director(self,user_id) -> bool:
        if user_id == 1:
            return True
        else:
            return False

    
    async def make_admin(self,user_id) -> UserSchema:
        user = await self.session.get(User, user_id)
        if user.admin == True:
           raise HTTPException(404,f"User {user.username} is already an admin")
        else:
            user.admin = True
            await self.session.commit()
            return UserSchema(id=user.id,
                username=user.username,
                email=user.email,
                phone_number=user.phone_number,
                operator_code=user.operator_code,
                time_zone=user.time_zone,
                admin=user.admin)

    async def delete_admin(self,user_id) -> UserSchema:
        user = await self.session.get(User, user_id)
        if not user.admin:
           raise HTTPException(404,f"User {user.username} is not  an admin")
        else:
            user.admin = False
        await self.session.commit()
        return UserSchema(id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            operator_code=user.operator_code,
            time_zone=user.time_zone,
            admin=user.admin)

    async def create_new_admin_user(self,user: UserAdminShema) -> UserSchema:
        db_user = await self.session.execute(select(User).filter(or_(User.email == user.email, User.username == user.username)))
        db_user = db_user.scalars().first()
        if db_user:
            raise HTTPException(404, 'username or email already in use')
        else:
            new_user = User(username=user.username, email=user.email, password=sha256.hash(user.password1), phone_number=user.phone_number, operator_code=user.operator_code,time_zone=user.time_zone, admin=user.admin)
            self.session.add(new_user)
            await self.session.commit()
            return UserSchema(id=new_user.id,
                username=new_user.username,
                email=new_user.email, 
                phone_number=user.phone_number,
                operator_code=user.operator_code,
                time_zone=user.time_zone,
                admin=new_user.admin)


async def get_user(session: AsyncSession = Depends(get_session), Token: str = Header()) -> User:
    email = auth_cls.decode_token(token=Token)
    user = await session.execute(select(User).filter(User.email == email))
    user = user.scalars().first()
    if user:
        return user
    else:
        raise HTTPException(404, 'user validation error')

