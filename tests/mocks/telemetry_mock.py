from unittest.mock import MagicMock
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter


class LogCapture:
    def __init__(self):
        self._logs = []

    def debug(self, message: str, fields: dict = None) -> None:
        self._logs.append(("debug", message, fields or {}))

    def info(self, message: str, fields: dict = None) -> None:
        self._logs.append(("info", message, fields or {}))

    def warning(self, message: str, fields: dict = None) -> None:
        self._logs.append(("warning", message, fields or {}))

    def error(self, message: str, fields: dict = None) -> None:
        self._logs.append(("error", message, fields or {}))

    # Утилиты для проверки
    def get_logs(self, level: str = None) -> list:
        if level is None:
            return self._logs
        return [log for log in self._logs if log[0] == level]

    def has_log(self, message: str, level: str = None) -> bool:
        logs = self.get_logs(level)
        return any(message in log[1] for log in logs)

    def clear(self) -> None:
        self._logs = []


class MockTelemetry:
    def __init__(self):
        self._logger = LogCapture()
        self._tracer = MagicMock(spec=Tracer)
        self._meter = MagicMock(spec=Meter)

    def logger(self) -> LogCapture:
        return self._logger

    def tracer(self) -> Tracer:
        return self._tracer

    def meter(self) -> Meter:
        return self._meter
