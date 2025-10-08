from unittest.mock import MagicMock
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter

from internal.interface import IOtelLogger, ITelemetry


class MockOtelLogger:
    def __init__(self):
        self._logs = []

    def debug(self, message: str, fields: dict = None) -> None:
        self._logs.append(("debug", message, fields))

    def info(self, message: str, fields: dict = None) -> None:
        self._logs.append(("info", message, fields))

    def warning(self, message: str, fields: dict = None) -> None:
        self._logs.append(("warning", message, fields))

    def error(self, message: str, fields: dict = None) -> None:
        self._logs.append(("error", message, fields))

    def get_logs(self) -> list:
        return self._logs

    def clear_logs(self) -> None:
        self._logs = []


class MockTelemetry:
    def __init__(self):
        self._tracer = MagicMock(spec=Tracer)
        self._meter = MagicMock(spec=Meter)
        self._logger = MockOtelLogger()

    def tracer(self) -> Tracer:
        return self._tracer

    def meter(self) -> Meter:
        return self._meter

    def logger(self) -> MockOtelLogger:
        return self._logger
