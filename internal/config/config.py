import os


class Config:
    def __init__(self):
        # Основные настройки приложения
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.service_name = os.getenv("KONTUR_ACCOUNT_CONTAINER_NAME", "kontur-account")
        self.http_port = os.getenv("KONTUR_ACCOUNT_PORT", "8000")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.root_path = os.getenv("ROOT_PATH", "/")
        self.prefix = os.getenv("KONTUR_ACCOUNT_PREFIX", "/api/account")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Настройки базы данных
        self.db_host = os.getenv("KONTUR_ACCOUNT_POSTGRES_CONTAINER_NAME", "localhost")
        self.db_port = "5432"
        self.db_name = os.getenv("KONTUR_ACCOUNT_POSTGRES_DB_NAME", "hr_interview")
        self.db_user = os.getenv("KONTUR_ACCOUNT_POSTGRES_USER", "postgres")
        self.db_pass = os.getenv("KONTUR_ACCOUNT_POSTGRES_PASSWORD", "password")

        # Настройки мониторинга и алертов
        self.alert_tg_bot_token = os.getenv("KONTUR_ALERT_TG_BOT_TOKEN", "")
        self.alert_tg_chat_id = os.getenv("KONTUR_ALERT_TG_CHAT_ID", "")
        self.alert_tg_chat_thread_id = os.getenv("KONTUR_ALERT_TG_CHAT_THREAD_ID", "")
        self.grafana_url = os.getenv("KONTUR_GRAFANA_URL", "")

        self.monitoring_redis_host = os.getenv("KONTUR_MONITORING_REDIS_CONTAINER_NAME", "localhost")
        self.monitoring_redis_port = int(os.getenv("KONTUR_MONITORING_REDIS_PORT", "6379"))
        self.monitoring_redis_db = int(os.getenv("KONTUR_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB", "0"))
        self.monitoring_redis_password = os.getenv("KONTUR_MONITORING_REDIS_PASSWORD", "")

        # Настройки OpenTelemetry
        self.otlp_host = os.getenv("KONTUR_OTEL_COLLECTOR_CONTAINER_NAME", "kontur-otel-collector")
        self.otlp_port = int(os.getenv("KONTUR_OTEL_COLLECTOR_GRPC_PORT", "4317"))

        # Настройки авторизации
        self.kontur_authorization_host = os.getenv("KONTUR_AUTHORIZATION_CONTAINER_NAME", "kontur-authorization-postgres")
        self.kontur_authorization_port = os.getenv("KONTUR_AUTHORIZATION_PORT", "8001")
        self.password_secret_key = os.getenv("KONTUR_PASSWORD_SECRET_KEY", "default-secret-key-change-me")

        self.openai_api_key = os.getenv("OPENAI_API_KEY", None)