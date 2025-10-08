from unittest.mock import MagicMock
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter

from internal import interface


class MockTelemetry:
    def __init__(self):
        self._logger = MagicMock(spec=interface.IOtelLogger)
        self._tracer = MagicMock(spec=Tracer)
        self._meter = MagicMock(spec=Meter)

    def logger(self):
        return self._logger

    def tracer(self) -> Tracer:
        return self._tracer

    def meter(self) -> Meter:
        return self._meter
