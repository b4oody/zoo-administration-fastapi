from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserCreate, UserRead
from auth.security import hash_password, decode_token
from core.database import db_helper
from core.models import User


async def create_user(session: AsyncSession, user: UserCreate):
    hashed = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_username(session: AsyncSession, username: str):
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(db_helper.scoped_session_dependency)
) -> UserRead:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_user = await get_user_by_username(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(db_user)
