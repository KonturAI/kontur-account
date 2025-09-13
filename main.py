import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from pkg.client.internal.kontur_authorization.client import KonturAuthorizationClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.account.handler import AccountController

from internal.service.account.service import AccountService

from internal.repo.account.repo import AccountRepo

from internal.app.http.app import NewHTTP

from internal.config.config import Config

cfg = Config()

alert_manager = AlertManager(
    cfg.alert_tg_bot_token,
    cfg.service_name,
    cfg.alert_tg_chat_id,
    cfg.alert_tg_chat_thread_id,
    cfg.grafana_url,
    cfg.monitoring_redis_host,
    cfg.monitoring_redis_port,
    cfg.monitoring_redis_db,
    cfg.monitoring_redis_password
)

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
    alert_manager
)

# Инициализация клиентов
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)

# Инициализация клиентов
kontur_authorization_client = KonturAuthorizationClient(
    tel=tel,
    host=cfg.kontur_authorization_host,
    port=cfg.kontur_authorization_port,
)

# Инициализация репозиториев
account_repo = AccountRepo(tel, db)

# Инициализация сервисов
account_service = AccountService(
    tel=tel,
    account_repo=account_repo,
    kontur_authorization_client=kontur_authorization_client,
    password_secret_key=cfg.password_secret_key
)


# Инициализация контроллеров
account_controller = AccountController(tel, account_service)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, kontur_authorization_client, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db=db,
        account_controller=account_controller,
        http_middleware=http_middleware,
        prefix=cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)