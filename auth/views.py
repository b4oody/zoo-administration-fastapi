from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_user, get_user_by_username, get_current_user
from auth.schemas import UserCreate, UserRead, Token
from auth.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from core.database import db_helper

# from users.schemas import User, UserCreate

router = APIRouter(prefix="/api/v1/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    db_user = await get_user_by_username(session, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(session, user)


@router.post("/login", response_model=Token)
async def login(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    db_user = await get_user_by_username(session, username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: UserRead = Depends(get_current_user)):
    return current_user
