# Документация по тестовой инфраструктуре

Этот документ описывает структуру и использование тестовой инфраструктуры проекта loom-account.

## 📁 Структура

```
tests/
├── unit/                          # Юнит-тесты
│   ├── service/                   # Тесты сервисов (моки: repo + clients)
│   ├── repo/                      # Тесты репо (моки: DB)
│   ├── controller/                # Тесты контроллеров (моки: services)
│   └── conftest.py                # Fixtures для unit-тестов
│
├── integration/                   # Интеграционные тесты
│   ├── api/                       # API тесты (TestClient + моки)
│   ├── repo/                      # Репо с реальной БД (testcontainers)
│   ├── clients/                   # Тесты клиентов микросервисов (respx)
│   └── conftest.py                # Fixtures для integration-тестов
│
├── fixtures/                      # Переиспользуемые fixtures
│   └── conftest.py
│
├── factories/                     # Фабрики тестовых данных
│   ├── account_factory.py
│   └── auth_factory.py
│
├── mocks/                         # Моки зависимостей
│   ├── telemetry_mock.py
│   ├── loom_authorization_mock.py
│   ├── db_mock.py
│   └── repo_mock.py
│
├── utils/                         # Вспомогательные утилиты
│   ├── helpers.py
│   └── assertions.py
│
├── conftest.py                    # Главный конфиг pytest
└── README.md
```

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов

```bash
pytest
```

### Запуск по типам

```bash
# Только юнит-тесты (быстрые)
pytest -m unit

# Только интеграционные тесты
pytest -m integration

# API тесты
pytest -m api

# Тесты репо с реальной БД
pytest -m repo

# Тесты клиентов
pytest -m client
```

### Запуск конкретных тестов

```bash
# Конкретный файл
pytest tests/unit/service/test_account_service_example.py -v

# Конкретная директория
pytest tests/unit/service/ -v

# Конкретный тест
pytest tests/unit/service/test_account_service_example.py::TestAccountServiceRegister::test_register_success -v
```

## 📝 Типы тестов

### 1. Юнит-тесты (Unit Tests)

**Цель:** Изолированное тестирование отдельных компонентов

**Что мокируется:**
- **Service тесты:** Мокируем repo + внешние клиенты
- **Repo тесты:** Мокируем DB
- **Controller тесты:** Мокируем services

**Пример:**
```python
@pytest.mark.unit
async def test_register_success(
    account_service,           # Реальный сервис
    mock_account_repo,         # Мок репо
    mock_loom_authorization_client  # Мок клиента
):
    # Test logic
    pass
```

### 2. API интеграционные тесты

**Цель:** Тестирование HTTP API через TestClient

**Что мокируется:**
- Репозитории (через mock_account_repo)
- Внешние сервисы (mock_loom_authorization_client)

**Что реально:**
- FastAPI приложение
- Контроллеры
- Сервисы
- HTTP flow

**Пример:**
```python
@pytest.mark.integration
@pytest.mark.api
async def test_register_returns_201(test_client, api_headers):
    response = test_client.post("/register", json=payload, headers=api_headers)
    assert response.status_code == 201
```

### 3. Интеграционные тесты репо

**Цель:** Проверка работы с реальной БД

**Что реально:**
- PostgreSQL в Docker (testcontainers)
- Миграции
- SQL запросы

**Пример:**
```python
@pytest.mark.integration
@pytest.mark.repo
async def test_create_and_retrieve_account(test_account_repo):
    account_id = await test_account_repo.create_account("user", "pass")
    accounts = await test_account_repo.account_by_id(account_id)
    assert len(accounts) == 1
```

⚠️ **Внимание:** Эти тесты медленные, т.к. запускают Docker контейнер!

### 4. Тесты клиентов микросервисов

**Цель:** Проверка корректности HTTP запросов к другим сервисам

**Что мокируется:**
- HTTP запросы (через respx)

**Что реально:**
- Логика клиента
- Сериализация/десериализация

**Пример:**
```python
@pytest.mark.integration
@pytest.mark.client
async def test_authorization_success(
    respx_mock,
    loom_authorization_client,
    mock_authorization_response
):
    respx.post("http://localhost:8080/api/authorization").mock(
        return_value=mock_authorization_response()
    )
    result = await loom_authorization_client.authorization(1, False, "employee")
    assert result.access_token == "test_access"
```

## 🔧 Доступные Fixtures

### Базовые моки (tests/conftest.py)

- `mock_telemetry` - Мок telemetry
- `mock_logger` - Мок logger
- `mock_loom_authorization_client` - Мок клиента авторизации
- `mock_db` - Мок БД
- `mock_account_repo` - Мок репозитория аккаунтов
- `test_password_secret` - Секретный ключ для тестов
- `log_context` - ContextVar для логов

### Фабрики (tests/fixtures/conftest.py)

- `account_factory` - Фабрика Account
- `account_with_two_fa_factory` - Фабрика Account с 2FA
- `jwt_tokens_factory` - Фабрика JWT токенов
- `authorization_data_factory` - Фабрика AuthorizationData
- `authorization_data_dto_factory` - Фабрика AuthorizationDataDTO

### Готовые данные

- `test_account` - Готовый тестовый аккаунт
- `test_account_with_2fa` - Готовый аккаунт с 2FA
- `test_jwt_tokens` - Готовые JWT токены

### Unit тесты (tests/unit/conftest.py)

- `account_service` - AccountService с моками
- `account_repo` - AccountRepo с мок БД
- `account_controller` - AccountController с мок сервисом
- `mock_account_service` - Мок сервиса для контроллера

### Integration тесты (tests/integration/conftest.py)

- `postgres_container` - PostgreSQL testcontainer
- `test_db` - Реальное подключение к тестовой БД
- `test_account_repo` - AccountRepo с реальной БД

### API тесты (tests/integration/api/conftest.py)

- `test_client` - FastAPI TestClient
- `api_headers` - Базовые HTTP заголовки

### Клиенты (tests/integration/clients/conftest.py)

- `respx_mock` - Respx мок для HTTP
- `loom_authorization_client` - Реальный клиент
- `mock_authorization_response` - Мок ответа /authorization
- `mock_check_authorization_response` - Мок ответа /check

## 🏭 Использование фабрик

Фабрики позволяют легко создавать тестовые данные:

```python
from tests.factories.account_factory import AccountFactory

# Создать аккаунт с дефолтными значениями
account = AccountFactory()

# Создать аккаунт с кастомными значениями
account = AccountFactory(login="custom_user", password="custom_pass")

# Создать несколько аккаунтов
accounts = AccountFactory.build_batch(5)
```

## 🎭 Работа с моками

### Настройка ответов мока

```python
# Mock LoomAuthorizationClient
mock_loom_authorization_client.set_authorization_response(
    account_id=1,
    two_fa_status=False,
    role="employee",
    response=JWTTokens(access_token="test", refresh_token="test")
)

# Mock AccountRepo
mock_account_repo.add_account(test_account)

# Mock DB
mock_db.set_select_response(query, [mock_row])
```

### Проверка вызовов мока

```python
# Получить историю вызовов
calls = mock_account_repo.get_call_history()

# Проверить вызовы
assert len(calls) == 2
assert calls[0]["method"] == "account_by_login"
assert calls[1]["method"] == "create_account"
```

## 🛠 Вспомогательные утилиты

### helpers.py

```python
from tests.utils.helpers import hash_password, create_mock_db_row

# Хеширование пароля для тестов
hashed = hash_password("password", "secret_key")

# Создание мок строки из БД
row = create_mock_db_row(id=1, login="user", password="hash")
```

### assertions.py

```python
from tests.utils.assertions import assert_model_equal

# Сравнить модели, игнорируя created_at
assert_model_equal(account1, account2, exclude_fields={'created_at'})
```

## 📊 Лучшие практики

### 1. Именование тестов

```python
# ✅ Хорошо
async def test_register_success()
async def test_register_duplicate_login()
async def test_login_invalid_password()

# ❌ Плохо
async def test_1()
async def test_user()
```

### 2. Структура теста (Arrange-Act-Assert)

```python
async def test_example(account_service, mock_account_repo):
    # Arrange - подготовка данных
    login = "test_user"
    password = "test_password"

    # Act - выполнение тестируемого метода
    result = await account_service.register(login, password)

    # Assert - проверка результатов
    assert result.account_id > 0
```

### 3. Использование маркеров

```python
@pytest.mark.unit
async def test_service_method():
    pass

@pytest.mark.integration
@pytest.mark.api
async def test_api_endpoint():
    pass

@pytest.mark.integration
@pytest.mark.repo
async def test_database_operation():
    pass
```

### 4. Изоляция тестов

- Каждый тест должен быть независимым
- Используйте фабрики для создания свежих данных
- Моки автоматически очищаются после каждого теста

## 🐳 Testcontainers

Для интеграционных тестов репо используется testcontainers:

- Автоматически запускает PostgreSQL в Docker
- Запускает миграции
- Изолирует тесты
- Автоматически удаляет контейнер после тестов

⚠️ **Требования:**
- Docker должен быть запущен
- Права на создание контейнеров

## 🔍 Отладка тестов

### Подробный вывод

```bash
pytest -vv -s
```

### Остановка на первой ошибке

```bash
pytest -x
```

### Запуск последнего упавшего теста

```bash
pytest --lf
```

### Отладка с pdb

```python
async def test_example():
    import pdb; pdb.set_trace()
    # ...
```

## 📚 Примеры

Все типы тестов имеют файлы с примерами:
- `tests/unit/service/test_account_service_example.py`
- `tests/unit/repo/test_account_repo_example.py`
- `tests/unit/controller/test_account_controller_example.py`
- `tests/integration/api/test_account_api_example.py`
- `tests/integration/repo/test_account_repo_integration_example.py`
- `tests/integration/clients/test_loom_authorization_client_example.py`

## 🤝 Contribution

При добавлении новых тестов:
1. Следуйте существующей структуре
2. Используйте существующие fixtures и моки
3. Добавляйте соответствующие маркеры
4. Документируйте сложные тесты

## ❓ FAQ

**Q: Какие тесты писать сначала?**
A: Начните с unit-тестов сервисов, затем API интеграционные тесты.

**Q: Когда использовать testcontainers?**
A: Только для тестов репо, где нужна реальная БД и валидация SQL.

**Q: Как мокировать время?**
A: Используйте `freezegun` (уже в зависимостях).

**Q: Нужно ли тестировать все методы?**
A: Критичные пути - обязательно. Остальное - по приоритету.
