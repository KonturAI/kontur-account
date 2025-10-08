import pytest
from testcontainers.postgres import PostgresContainer

from infrastructure.pg.pg import PG
from internal.repo.account.repo import AccountRepo



@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture
async def test_db(postgres_container, mock_telemetry):
    db = PG(
        tel=mock_telemetry,
        db_user=postgres_container.username,
        db_pass=postgres_container.password,
        db_host=postgres_container.get_container_host_ip(),
        db_port=postgres_container.get_exposed_port(5432),
        db_name=postgres_container.dbname
    )

    # Запуск миграций
    from internal.migration.manager import MigrationManager
    migration_manager = MigrationManager(db)
    await migration_manager.migrate()

    yield db

    # Очистка после теста
    # Можно добавить cleanup логику если нужно


@pytest.fixture
async def test_account_repo(test_db, mock_telemetry):
    return AccountRepo(
        tel=mock_telemetry,
        db=test_db
    )
