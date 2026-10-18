from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from typing import Annotated
from app.setting import setting

engine = create_async_engine(url=setting.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
        print("db closed successfully")


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]