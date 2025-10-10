from contextvars import ContextVar

import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import AlertManager, Telemetry
from internal.app.http.app import NewHTTP
from internal.config.config import Config
from internal.controller.http.handler.account.handler import AccountController
from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.repo.account.repo import AccountRepo
from internal.service.account.service import AccountService
from pkg.client.internal.loom_authorization.client import LoomAuthorizationClient

cfg = Config()

log_context: ContextVar[dict] = ContextVar("log_context", default={})

alert_manager = AlertManager(
    cfg.alert_tg_bot_token,
    cfg.service_name,
    cfg.alert_tg_chat_id,
    cfg.alert_tg_chat_thread_id,
    cfg.grafana_url,
    cfg.monitoring_redis_host,
    cfg.monitoring_redis_port,
    cfg.monitoring_redis_db,
    cfg.monitoring_redis_password,
)

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
    log_context,
    alert_manager,
)

# Инициализация клиентов
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)

# Инициализация клиентов
loom_authorization_client = LoomAuthorizationClient(
    tel=tel,
    host=cfg.loom_authorization_host,
    port=cfg.loom_authorization_port,
    log_context=log_context,
)

# Инициализация репозиториев
account_repo = AccountRepo(tel, db)

# Инициализация сервисов
account_service = AccountService(
    tel=tel,
    account_repo=account_repo,
    loom_authorization_client=loom_authorization_client,
    password_secret_key=cfg.password_secret_key,
)

# Инициализация контроллеров
account_controller = AccountController(tel, account_service)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, loom_authorization_client, cfg.prefix, log_context)

app = NewHTTP(
    db=db,
    account_controller=account_controller,
    http_middleware=http_middleware,
    prefix=cfg.prefix,
)

if __name__ == "__main__":
    if cfg.environment == "prod":
        workers = 2
    else:
        workers = 1

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(cfg.http_port),
        workers=workers,
        loop="uvloop",
        access_log=False,
    )
