import io
from abc import abstractmethod
from typing import Protocol, Sequence, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer
from starlette.responses import StreamingResponse

from internal import model


class IOtelLogger(Protocol):
    @abstractmethod
    def debug(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def warning(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, fields: dict = None) -> None:
        pass


class ITelemetry(Protocol):
    @abstractmethod
    def tracer(self) -> Tracer:
        pass

    @abstractmethod
    def meter(self) -> Meter:
        pass

    @abstractmethod
    def logger(self) -> IOtelLogger:
        pass


class IHttpMiddleware(Protocol):
    @abstractmethod
    def trace_middleware01(self, app: FastAPI): pass

    @abstractmethod
    def metrics_middleware02(self, app: FastAPI): pass

    @abstractmethod
    def logger_middleware03(self, app: FastAPI): pass


class IRedis(Protocol):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool: pass

    @abstractmethod
    async def get(self, key: str, default: Any = None) -> Any: pass


class IStorage(Protocol):
    @abstractmethod
    async def delete(self, fid: str, name: str): pass

    @abstractmethod
    async def download(self, fid: str, name: str) -> tuple[io.BytesIO, str]: pass

    @abstractmethod
    async def upload(self, file: io.BytesIO, name: str) -> model.AsyncWeedOperationResponse: pass

    @abstractmethod
    async def update(self, file: io.BytesIO, fid: str, name: str): pass


class IDB(Protocol):

    @abstractmethod
    async def insert(self, query: str, query_params: dict) -> int: pass

    @abstractmethod
    async def delete(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def update(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def select(self, query: str, query_params: dict) -> Sequence[Any]: pass

    @abstractmethod
    async def multi_query(self, queries: list[str]) -> None: pass


class ILLMClient(Protocol):
    @abstractmethod
    async def generate_str(
            self,
            history: list[model.Message],
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> str: pass

    @abstractmethod
    async def generate_json(
            self,
            history: list[model.Message],
            system_prompt: str,
            temperature: float,
            llm_model: str,
            pdf_file: bytes = None,
    ) -> dict: pass

    @abstractmethod
    async def transcribe_audio(
            self,
            audio_file: bytes,
            filename: str = "audio.wav"
    ) -> str: pass

    @abstractmethod
    async def text_to_speech(
            self,
            text: str,
            voice: str = "alloy",
            tts_model: str = "tts-1-hd"
    ) -> bytes: pass

class ITelegramClient(Protocol):
    @abstractmethod
    async def generate_qr_code(self) -> io.BytesIO: pass

    @abstractmethod
    async def qr_code_status(self) -> tuple[str, str]: pass

    @abstractmethod
    async def start(self): pass

    @abstractmethod
    async def send_message_to_telegram(
            self,
            tg_user_data: str,
            text: str
    ): pass

class ITelegramHTTPController(Protocol):
    @abstractmethod
    async def generate_qr_code(self) -> StreamingResponse:
        pass

    @abstractmethod
    async def check_qr_status(self) -> JSONResponse:
        pass

    @abstractmethod
    async def start_telegram_client(self) -> JSONResponse:
        pass

