from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    sendgrid_to_email: str = ""

    ml_client_id: str = ""
    ml_client_secret: str = ""

    ebay_app_id: str = ""  # eBay Developer App ID — registrar em developer.ebay.com (grátis)

    evolution_api_url: str = ""       # ex: https://evolution-xxx.railway.app
    evolution_api_key: str = ""       # AUTHENTICATION_API_KEY do Railway
    evolution_instance: str = "hunter"
    whatsapp_number: str = ""         # número com DDI: 5511999999999

    database_url: str = "sqlite+aiosqlite:///hunter.db"

    min_margin_buy: float = 0.40
    min_margin_negotiate: float = 0.20
    min_score_buy: int = 60
    min_score_notify: int = 65

    scan_interval_minutes: int = 30
    circuit_breaker_failures: int = 3
    circuit_breaker_pause_minutes: int = 60

    # Dashboard auth
    dashboard_user: str = "admin"
    dashboard_password: str = "hunter2024"
    dashboard_secret_key: str = "hunter-master-secret-change-me"


settings = Settings()
