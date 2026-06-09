from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Обратите внимание на +psycopg (это асинхронный драйвер)
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Зависимость для получения сессии (удобно для FastAPI и бота)
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session