# Руководство по использованию линтеров

## Установленные инструменты

- **Ruff** - быстрый линтер и форматтер (замена flake8, black, isort)
- **MyPy** - статическая проверка типов
- **Bandit** - проверка безопасности кода
- **Pre-commit** - автоматический запуск линтеров перед коммитом

---

## Быстрый старт

### 1. Проверить весь проект

```bash
# Ruff - линтинг + форматирование
ruff check .                    # Показать все проблемы
ruff check . --fix              # Автоматически исправить что можно
ruff format .                   # Отформатировать код

# MyPy - проверка типов
mypy .

# Bandit - проверка безопасности
bandit -r . -f txt
```

### 2. Проверить конкретный файл

```bash
ruff check internal/service/account/service.py
mypy internal/service/account/service.py
bandit internal/service/account/service.py
```

### 3. Проверить конкретную папку

```bash
ruff check internal/service/ --fix
mypy internal/service/
```

---

## Ruff - основной линтер

### Базовые команды

```bash
# Проверить код
ruff check .

# Показать что будет исправлено (dry-run)
ruff check . --fix --diff

# Исправить автоматически
ruff check . --fix

# Форматировать код (как black)
ruff format .

# Проверить форматирование без изменений
ruff format . --check
```

### Полезные опции

```bash
# Показать только ошибки (без предупреждений)
ruff check . --select E,F

# Игнорировать конкретные правила
ruff check . --ignore E501,F401

# Компактный вывод
ruff check . --output-format=concise

# Подробный вывод с объяснениями
ruff check . --output-format=full

# Показать статистику
ruff check . --statistics
```

### Проверка перед коммитом

```bash
# Быстрая проверка всего что изменено
git diff --name-only --cached | xargs ruff check
git diff --name-only --cached | xargs ruff format --check
```

---

## MyPy - проверка типов

### Базовые команды

```bash
# Проверить весь проект
mypy .

# Проверить конкретный файл
mypy internal/service/account/service.py

# Показать больше информации
mypy . --show-error-codes --pretty

# Игнорировать отсутствующие импорты
mypy . --ignore-missing-imports
```

### Полезные опции

```bash
# Показать покрытие типами
mypy . --html-report ./mypy-report
mypy . --txt-report ./mypy-report

# Строгий режим
mypy . --strict

# Проверить только измененные файлы
mypy $(git diff --name-only --cached | grep '\.py$')
```

---

## Bandit - проверка безопасности

### Базовые команды

```bash
# Проверить весь проект
bandit -r .

# С конфигурацией из pyproject.toml
bandit -r . -c pyproject.toml

# Разные форматы вывода
bandit -r . -f txt              # Текстовый формат
bandit -r . -f json             # JSON формат
bandit -r . -f html -o report.html  # HTML отчет
```

### Полезные опции

```bash
# Показать только высокую и среднюю серьезность
bandit -r . -ll

# Игнорировать конкретные тесты
bandit -r . -s B101,B601

# Показать только высокую серьезность
bandit -r . -lll

# Verbose режим
bandit -r . -v
```

---

## Pre-commit - автоматическая проверка

Pre-commit автоматически запускается при `git commit`. Чтобы запустить вручную:

### Команды pre-commit

```bash
# Запустить на всех файлах
pre-commit run --all-files

# Запустить на staged файлах
pre-commit run

# Запустить конкретный хук
pre-commit run ruff --all-files
pre-commit run mypy --all-files
pre-commit run bandit --all-files

# Обновить версии хуков
pre-commit autoupdate

# Пропустить pre-commit при коммите (не рекомендуется)
git commit --no-verify
```

---

## Рабочий процесс (Workflow)

### При разработке

```bash
# 1. Пишете код...

# 2. Быстрая проверка и автофикс
ruff check . --fix
ruff format .

# 3. Проверка типов
mypy .

# 4. Если все ок, коммитите
git add .
git commit -m "feat: add new feature"
# Pre-commit автоматически запустится
```

### Если pre-commit нашел проблемы

```bash
# Pre-commit автоматически исправит что может
# Если есть неисправленные проблемы:

# 1. Посмотрите что не так
git diff

# 2. Добавьте автофиксы
git add .

# 3. Или исправьте вручную
# ... редактирование файлов ...

# 4. Коммитите снова
git commit
```

### Периодическая проверка всего проекта

```bash
# Запустить все проверки
pre-commit run --all-files

# Или по отдельности
ruff check . --fix
ruff format .
mypy .
bandit -r . -c pyproject.toml
```

---

## Интеграция с CI/CD

Пример для GitHub Actions (`.github/workflows/lint.yml`):

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff mypy bandit

      - name: Run Ruff
        run: ruff check .

      - name: Run MyPy
        run: mypy .

      - name: Run Bandit
        run: bandit -r . -c pyproject.toml
```

---

## Игнорирование ошибок

### В коде (inline)

```python
# Ruff
from typing import *  # noqa: F403
import unused_module  # noqa: F401

# MyPy
x = 1  # type: ignore
y: Any = get_data()  # type: ignore[no-untyped-call]

# Bandit
password = "test"  # nosec B105
```

### В конфигурации

Редактируйте `pyproject.toml`:

```toml
[tool.ruff.lint]
ignore = [
    "E501",  # line too long
    "F401",  # unused import
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # assert in tests is ok

[tool.mypy]
[[tool.mypy.overrides]]
module = "problematic_module.*"
ignore_errors = true
```

---

## Полезные алиасы

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
# Ruff
alias rl='ruff check .'
alias rf='ruff check . --fix'
alias rfmt='ruff format .'

# MyPy
alias mt='mypy .'

# Bandit
alias sec='bandit -r . -c pyproject.toml'

# Pre-commit
alias pc='pre-commit run --all-files'

# Все вместе
alias lint='ruff check . --fix && ruff format . && mypy . && bandit -r . -c pyproject.toml'
```

---

## FAQ

### Слишком много ошибок, что делать?

1. Запустите автофикс: `ruff check . --fix`
2. Отформатируйте: `ruff format .`
3. Посмотрите что осталось: `ruff check . --output-format=grouped`
4. Исправляйте по категориям (сначала импорты, потом типы, и т.д.)

### MyPy жалуется на внешние библиотеки

Добавьте в `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["library_name.*"]
ignore_missing_imports = true
```

### Bandit находит false-positive

Используйте `# nosec` или добавьте в `pyproject.toml`:

```toml
[tool.bandit]
skips = ["B101", "B601"]
```

### Pre-commit слишком медленный

Отключите медленные хуки (например, mypy на всех файлах) и запускайте их в CI/CD.

---

## Дополнительные ресурсы

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
