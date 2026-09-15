import os

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("BOT_TOKEN", "123456:test-token")
os.environ.setdefault("BOT_INTERNAL_TOKEN", "test-bot-secret")
os.environ.setdefault("COOKIE_SECURE", "false")

import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.auth.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.admin import Admin
from kazgaza_shared import AdminRole


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    from app.core.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def super_admin(db_session):
    admin = Admin(
        name="Super Admin",
        email="super@kazgaza.kz",
        password_hash=hash_password("supersecret123"),
        role=AdminRole.SUPER_ADMIN,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def dispatcher_admin(db_session):
    admin = Admin(
        name="Dispatcher",
        email="dispatcher@kazgaza.kz",
        password_hash=hash_password("dispatcher123"),
        role=AdminRole.DISPATCHER,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def operator_admin(db_session):
    admin = Admin(
        name="Operator",
        email="operator@kazgaza.kz",
        password_hash=hash_password("operator123"),
        role=AdminRole.OPERATOR,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


async def login(client: AsyncClient, email: str, password: str) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    client.headers["X-CSRF-Token"] = data["csrf_token"]
    return data
