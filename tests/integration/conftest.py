import pytest
from testcontainers.postgres import PostgresContainer
import asyncio

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry
from internal.migration.manager import MigrationManager
from internal.config.config import Config
from internal.repo.account.repo import AccountRepo


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def tel(log_context):
    cfg = Config()
    return Telemetry(
        cfg.log_level,
        cfg.root_path,
        cfg.environment,
        cfg.service_name,
        cfg.service_version,
        cfg.otlp_host,
        cfg.otlp_port,
        log_context,
    )


@pytest.fixture(scope="session")
def session_db(postgres_container, tel):
    db = PG(
        tel=tel,
        db_user=postgres_container.username,
        db_pass=postgres_container.password,
        db_host=postgres_container.get_container_host_ip(),
        db_port=postgres_container.get_exposed_port(5432),
        db_name=postgres_container.dbname
    )

    async def run_migrations():
        migration_manager = MigrationManager(db)
        await migration_manager.migrate()

    asyncio.run(run_migrations())

    return db


@pytest.fixture
async def test_db(session_db):
    yield session_db

    await session_db.delete("TRUNCATE TABLE accounts RESTART IDENTITY CASCADE", {})


@pytest.fixture
def account_repo(tel, test_db):
    return AccountRepo(
        tel=tel,
        db=test_db
    )
