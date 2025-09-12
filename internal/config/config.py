import os


class Config:
    def __init__(self):
        # Основные настройки приложения
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.service_name = os.getenv("SERVICE_NAME", "kontur-account")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.root_path = os.getenv("ROOT_PATH", "/")
        self.http_port = os.getenv("HTTP_PORT", "8000")
        self.prefix = os.getenv("PREFIX", "/api/v1")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Настройки базы данных
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "hr_interview")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_pass = os.getenv("DB_PASSWORD", "password")

        # Настройки мониторинга и алертов
        self.alert_tg_bot_token = os.getenv("ALERT_TG_BOT_TOKEN", "")
        self.alert_tg_chat_id = os.getenv("ALERT_TG_CHAT_ID", "")
        self.alert_tg_chat_thread_id = os.getenv("ALERT_TG_CHAT_THREAD_ID", "")
        self.grafana_url = os.getenv("GRAFANA_URL", "")

        self.monitoring_redis_host = os.getenv("MONITORING_REDIS_HOST", "localhost")
        self.monitoring_redis_port = int(os.getenv("MONITORING_REDIS_PORT", "6379"))
        self.monitoring_redis_db = int(os.getenv("MONITORING_REDIS_DB", "0"))
        self.monitoring_redis_password = os.getenv("MONITORING_REDIS_PASSWORD", "")

        # Настройки OpenTelemetry
        self.otlp_host = os.getenv("OTLP_HOST", "localhost")
        self.otlp_port = int(os.getenv("OTLP_PORT", "4317"))

        # Настройки авторизации
        self.kontur_authorization_host = os.getenv("KONTUR_AUTHORIZATION_BASE_URL", "http://localhost:8001")
        self.kontur_authorization_port = os.getenv("KONTUR_AUTHORIZATION_BASE_URL", "http://localhost:8001")
        self.password_secret_key = os.getenv("PASSWORD_SECRET_KEY", "default-secret-key-change-me")