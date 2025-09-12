import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.weedfs.weedfs import AsyncWeed
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from pkg.client.external.openai.client import GPTClient
from pkg.client.external.email.client import EmailClient
from pkg.client.external.telegram.client import LTelegramClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.vacancy.handler import VacancyController
from internal.controller.http.handler.interview.handler import InterviewController
from internal.controller.http.handler.organization.handler import TelegramHTTPController

from internal.service.vacancy.service import VacancyService
from internal.service.interview.service import InterviewService
from internal.service.interview.prompt import InterviewPromptGenerator
from internal.service.vacancy.prompt import VacancyPromptGenerator

from internal.repo.vacancy.repo import VacancyRepo
from internal.repo.interview.repo import InterviewRepo

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
storage = AsyncWeed(cfg.weed_master_host, cfg.weed_master_port)
llm_client = GPTClient(tel, cfg.openai_api_key)
email_client = EmailClient(
    tel=tel,
    smtp_host=cfg.smtp_host,
    smtp_port=cfg.smtp_port,
    smtp_user=cfg.smtp_user,
    smtp_password=cfg.smtp_password,
    use_tls=cfg.smtp_use_tls
)
telegram_client = LTelegramClient(tel, cfg.tg_api_id, cfg.tg_api_hash, cfg.tg_session_string)

# Инициализация репозиториев
vacancy_repo = VacancyRepo(tel, db)
interview_repo = InterviewRepo(tel, db)

# Инициализация сервисов
interview_prompt_generator = InterviewPromptGenerator(tel)
vacancy_prompt_generator = VacancyPromptGenerator(tel)
vacancy_service = VacancyService(
    tel,
    vacancy_repo,
    interview_repo,
    storage,
    vacancy_prompt_generator,
    llm_client,
    email_client,
    telegram_client
)

interview_service = InterviewService(
    tel,
    vacancy_repo,
    interview_repo,
    interview_prompt_generator,
    llm_client,
    storage
)

# Инициализация контроллеров
vacancy_controller = VacancyController(tel, vacancy_service)
interview_controller = InterviewController(tel, interview_service)
telegram_controller = TelegramHTTPController(tel, telegram_client)

# Инициализация middleware
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        vacancy_controller,
        interview_controller,
        telegram_controller,
        telegram_client,
        http_middleware,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)