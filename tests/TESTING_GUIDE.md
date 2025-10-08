# Testing Guide

**Философия тестирования с pytest-mock для микросервисной архитектуры**

Этот гайд описывает подход к тестированию, который легко масштабируется на другие микросервисы.

---

## 🎯 Философия

### Ключевые принципы

1. **Используем pytest-mock для всех моков**
   - `mocker.AsyncMock(spec=Interface)` для type safety
   - Spec=Interface гарантирует правильные сигнатуры методов
   - Автоматический reset моков между тестами

2. **Factories для данных, Mocker для поведения**
   - Factory_boy для создания тестовых данных
   - pytest-mock для мокирования зависимостей
   - Четкое разделение ответственности

3. **Явность > Неявность**
   - Каждый мок настраивается явно
   - Нет магических дефолтных значений
   - Если тест упал, сразу понятно почему

4. **Простота > Сложность**
   - Избегаем кастомных моков (кроме telemetry)
   - Используем стандартные инструменты pytest
   - Код тестов должен быть проще production кода

5. **Isolation > Integration (в unit-тестах)**
   - Максимальная изоляция компонентов
   - Каждый unit-тест тестирует один компонент
   - Integration тесты - отдельно

---

## 📂 Структура тестов

```
tests/
├── conftest.py              # Главный conftest (базовые моки + factories)
│
├── unit/                    # Unit-тесты (быстрые, изолированные)
│   ├── conftest.py          # Фикстуры для unit-тестов
│   ├── service/             # Тесты сервисов (моки: repo + clients)
│   ├── repo/                # Тесты репо (моки: DB)
│   └── controller/          # Тесты контроллеров (моки: services)
│
├── integration/             # Integration тесты (медленные, реальные компоненты)
│   ├── conftest.py          # Фикстуры для integration
│   ├── api/                 # API тесты (TestClient + моки repo/clients)
│   ├── repo/                # Репо + реальная БД (testcontainers)
│   └── clients/             # Клиенты + respx для HTTP моков
│
├── factories/               # Factory_boy factories
│   ├── account_factory.py
│   └── auth_factory.py
│
├── mocks/                   # Только telemetry_mock (единственный кастомный)
│   └── telemetry_mock.py
│
└── utils/                   # Helpers и assertions
    ├── helpers.py
    └── assertions.py
```

### Почему такая структура?

- **conftest.py на каждом уровне** - четкая изоляция scope фикстур
- **Зеркалирование структуры проекта** - легко найти тесты
- **Минимум кастомных моков** - pytest-mock для всего (кроме telemetry)
- **Factories в одном месте** - переиспользуемые данные

---

## 🧪 Типы тестов

### 1. Unit-тесты

**Цель:** Изолированное тестирование одного компонента

| Тестируем | Реально | Мокируется |
|-----------|---------|------------|
| **Service** | Бизнес-логика сервиса | repo, clients, telemetry |
| **Repo** | SQL запросы, маппинг | DB, telemetry |
| **Controller** | HTTP обработка, валидация | services, telemetry |

**Пример:**
```python
@pytest.mark.unit
async def test_register_success(
    account_service,          # Реальный service
    mock_account_repo,        # Mock repo через pytest-mock
    mock_loom_authorization_client  # Mock client через pytest-mock
):
    # Arrange
    setup_account_repo_find_by_login(mock_account_repo, not_found=True)
    setup_account_repo_create(mock_account_repo, account_id=1)

    # Act
    result = await account_service.register("user", "password")

    # Assert
    assert_authorization_dto(result, account_id=1)
```

### 2. Integration-тесты

**Цель:** Проверка взаимодействия компонентов

**API тесты:**
- FastAPI TestClient
- Реальные контроллеры + сервисы
- Моки: repo, clients

**Repo тесты:**
- Реальная PostgreSQL (testcontainers)
- Реальные миграции
- Реальные SQL запросы

**Client тесты:**
- Реальная логика клиента
- respx для моков HTTP запросов
- Проверка сериализации/десериализации

---

## 🔧 Работа с pytest-mock

### Создание моков

```python
# ✅ Правильно - используем spec для type safety
@pytest.fixture
def mock_account_repo(mocker):
    from internal.interface import IAccountRepo
    return mocker.AsyncMock(spec=IAccountRepo)

# ❌ Неправильно - нет spec, нет type safety
@pytest.fixture
def mock_account_repo(mocker):
    return mocker.AsyncMock()
```

### Настройка моков

```python
# Вариант 1: Явная настройка
mock_account_repo.account_by_login.return_value = [account]

# Вариант 2: Через helper (рекомендуется)
from tests.utils.helpers import setup_account_repo_find_by_login
setup_account_repo_find_by_login(mock_account_repo, account=account)

# Вариант 3: Для complex cases
mock_account_repo.create_account.side_effect = [1, 2, 3]  # Разные ID для каждого вызова
```

### Проверка вызовов

```python
# Базовая проверка
mock_account_repo.create_account.assert_called_once()

# С параметрами
mock_account_repo.create_account.assert_called_once_with(
    login="user",
    password="hashed_password"
)

# Проверка количества вызовов
assert mock_account_repo.create_account.call_count == 2

# Проверка НЕ вызван
mock_account_repo.delete_account.assert_not_called()

# Частичная проверка (только определенные поля)
from tests.utils.assertions import assert_mock_called_with_fields
assert_mock_called_with_fields(
    mock_account_repo.create_account,
    login="user"  # проверяем только login
)
```

---

## 🏭 Factories (factory_boy)

### Создание

```python
# Базовый account
account = AccountFactory()

# С кастомными полями
account = AccountFactory(login="custom_user")

# С trait
account = AccountFactory(with_2fa=True)
account = AccountWithTwoFAFactory()  # Alias

# Batch
accounts = AccountFactory.create_batch(5)

# С параметром
old_account = AccountFactory(created_days_ago=365)
```

### Добавление новой Factory

1. Создайте factory class:
```python
# tests/factories/my_model_factory.py
import factory
from internal import model

class MyModelFactory(factory.Factory):
    class Meta:
        model = model.MyModel

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
```

2. Добавьте фикстуру в `tests/conftest.py`:
```python
@pytest.fixture
def my_model_factory():
    from tests.factories.my_model_factory import MyModelFactory
    return MyModelFactory

@pytest.fixture
def my_model(my_model_factory):
    return my_model_factory()
```

### Traits для разных состояний

```python
class AccountFactory(factory.Factory):
    class Params:
        # Trait
        with_2fa = Trait(
            google_two_fa_key=Faker("pystr", max_chars=32)
        )

        # Параметр
        created_days_ago = None

    @factory.lazy_attribute
    def created_at(self):
        if self.created_days_ago:
            return datetime.now() - timedelta(days=self.created_days_ago)
        return datetime.now()
```

---

## ✅ Assertions и Helpers

### Assertions для моделей

```python
from tests.utils.assertions import (
    assert_model_equal,
    assert_account_valid,
    assert_jwt_tokens,
    assert_authorization_dto
)

# Сравнить модели (с исключением полей)
assert_model_equal(account1, account2, exclude_fields={'created_at'})

# Проверить валидность
assert_account_valid(account)

# Проверить JWT tokens
assert_jwt_tokens(tokens, access_token="expected")

# Проверить DTO
assert_authorization_dto(dto, account_id=1)
```

### Helpers для setup

```python
from tests.utils.helpers import (
    setup_account_repo_find_by_login,
    setup_account_repo_create,
    setup_loom_auth_client_authorization,
    hash_password
)

# Setup repo
setup_account_repo_find_by_login(mock_repo, account=test_account)
setup_account_repo_find_by_login(mock_repo, not_found=True)

# Setup client
setup_loom_auth_client_authorization(mock_client, tokens=tokens)

# Hash password
hashed = hash_password("password", "secret")
```

---

## 📝 Best Practices

### 1. Структура теста (Arrange-Act-Assert)

```python
async def test_something(account_service, mock_account_repo):
    # ========== Arrange ==========
    # Подготовка данных и моков
    login = "test_user"
    setup_account_repo_find_by_login(mock_account_repo, not_found=True)

    # ========== Act ==========
    # Выполнение тестируемого метода
    result = await account_service.register(login, "password")

    # ========== Assert ==========
    # Проверка результатов
    assert result is not None
    assert result.account_id > 0
    mock_account_repo.create_account.assert_called_once()
```

### 2. Один тест = Одна проверка

```python
# ✅ Правильно - проверяем одно поведение
async def test_register_creates_account():
    # ...
    assert account_id > 0

async def test_register_returns_tokens():
    # ...
    assert_jwt_tokens(result)

# ❌ Неправильно - проверяем много вещей
async def test_register():
    # ... проверяем и account, и tokens, и логи, и моки
```

### 3. Явные и читаемые имена

```python
# ✅ Правильно
async def test_register_with_duplicate_login_raises_error():
    pass

async def test_login_with_invalid_password_returns_none():
    pass

# ❌ Неправильно
async def test_register_1():
    pass

async def test_error():
    pass
```

### 4. Используйте pytest.mark.parametrize

```python
@pytest.mark.parametrize("login,password,should_fail", [
    ("", "password", True),           # Empty login
    ("user", "", True),               # Empty password
    ("valid", "valid", False),        # Valid input
])
async def test_register_with_various_inputs(
    account_service,
    login,
    password,
    should_fail
):
    # ...
```

### 5. Группируйте тесты в классы

```python
@pytest.mark.unit
class TestAccountServiceRegister:
    """Все тесты для метода register()"""

    async def test_success(self):
        pass

    async def test_duplicate_login(self):
        pass

    async def test_invalid_password(self):
        pass
```

---

## 🔁 Переиспользование на других микросервисах

### Checklist для нового микросервиса

1. **Скопируйте структуру папок:**
   ```
   tests/
   ├── conftest.py
   ├── unit/
   │   └── conftest.py
   ├── integration/
   │   └── conftest.py
   ├── factories/
   ├── mocks/
   │   └── telemetry_mock.py  # Копируем as-is
   └── utils/
       ├── helpers.py          # Адаптируем под свои модели
       └── assertions.py       # Адаптируем под свои модели
   ```

2. **Скопируйте базовые файлы:**
   - `tests/conftest.py` - адаптируйте моки под свои интерфейсы
   - `tests/mocks/telemetry_mock.py` - копируем без изменений
   - `tests/unit/conftest.py` - адаптируйте под свои layers

3. **Создайте Factories для своих моделей:**
   - Следуйте pattern из `account_factory.py`
   - Используйте traits для разных состояний

4. **Адаптируйте helpers.py:**
   - Замените `setup_account_repo_*` на `setup_<your_entity>_repo_*`
   - Добавьте helpers для своих clients

5. **Адаптируйте assertions.py:**
   - Замените `assert_account_*` на `assert_<your_entity>_*`
   - Оставьте generic assertions (assert_model_equal, etc)

6. **Создайте первый тест:**
   - Скопируйте `test_account_service.py` как template
   - Адаптируйте под свой сервис

### Пример для другого микросервиса (loom-order)

```python
# tests/conftest.py
@pytest.fixture
def mock_order_repo(mocker):
    from internal.interface import IOrderRepo
    return mocker.AsyncMock(spec=IOrderRepo)

# tests/factories/order_factory.py
class OrderFactory(factory.Factory):
    class Meta:
        model = model.Order

    id = factory.Sequence(lambda n: n + 1)
    user_id = Faker("random_int", min=1, max=1000)
    status = "pending"

# tests/utils/helpers.py
def setup_order_repo_find_by_id(mock_repo, order=None, not_found=False):
    if not_found:
        mock_repo.order_by_id.return_value = []
    elif order:
        mock_repo.order_by_id.return_value = [order]
```

---

## 🚀 Запуск тестов

```bash
# Все тесты
pytest

# Только unit
pytest -m unit

# Только integration
pytest -m integration

# Конкретный файл
pytest tests/unit/service/test_account_service.py -v

# С coverage
pytest --cov=internal --cov-report=html

# Быстрый feedback loop (fail fast)
pytest -x --ff
```

---

## ❓ FAQ

**Q: Когда использовать кастомный мок vs pytest-mock?**

A: Почти никогда. Единственное исключение - telemetry, потому что нужна удобная проверка логов. Для всего остального - pytest-mock.

**Q: Нужно ли мокировать telemetry в каждом тесте?**

A: Нет, `mock_telemetry` фикстура уже есть в `tests/conftest.py` и доступна везде.

**Q: Как тестировать асинхронный код?**

A: Просто используйте `async def test_*` и `await`. pytest-asyncio все сделает.

**Q: Что делать если тест иногда падает (flaky)?**

A: Это признак проблем с изоляцией. Проверьте что:
1. Моки сбрасываются между тестами (pytest-mock делает это автоматически)
2. Нет shared state между тестами
3. Нет race conditions в асинхронном коде

**Q: Сколько assertions в одном тесте?**

A: Желательно 1-3. Если больше - возможно тест проверяет слишком много. Разбейте на несколько тестов.

---

## 📚 Дополнительные ресурсы

- [pytest documentation](https://docs.pytest.org/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [factory_boy documentation](https://factoryboy.readthedocs.io/)
- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)

---

## 🎓 Примеры

Смотрите `tests/unit/service/test_account_service.py` для полного примера с best practices.

Ключевые моменты в примере:
- ✅ Использование pytest-mock
- ✅ Arrange-Act-Assert структура
- ✅ Helpers для setup
- ✅ Assertions для проверок
- ✅ Parametrize для edge cases
- ✅ Группировка в классы
- ✅ Явные и читаемые имена
