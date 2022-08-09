import asyncio
from os import path

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from website.core import crud, schemas
from website.core.config import SQLALCHEMY_DATABASE_URL, SYNC_SQLALCHEMY_DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=False)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_admin():
    async with async_session() as db:
        try:
            all_permissions = ["admin", "school", "program", "team", "coach", "volunteer"]
            for permission in all_permissions:
                await crud.create_permission(db, schemas.Permission(name=permission))
                await crud.create_user_permission_link(db, schemas.UserPermissions(user_id=1, permission_name=permission))
        finally:
            await db.close()


async def init_database():
    await init_models()
    await init_admin()


if not path.exists("./database.db"):
    asyncio.create_task(init_database())
    print("Created Database!")

# sync_engine = create_engine(SYNC_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# sync_session = sessionmaker(bind=sync_engine, expire_on_commit=False, autocommit=False, autoflush=False)
#
#
# def get_sync_session():
#     db = sync_session()
#     try:
#         yield db
#     finally:
#         db.close()
