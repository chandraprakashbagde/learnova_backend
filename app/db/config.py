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
        # Must be awaited: AsyncSession.close() is a coroutine. Without it the
        # pooled connection is never released and the engine hits its queue-pool
        # limit (15) after ~15 requests, 500-ing every call that follows.
        await session.close()
        print("db closed successfully")


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]