from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TradeMind API"
    app_env: str = "development"
    app_version: str = "0.1.0"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    binance_base_url: str = "https://api.binance.com"
    gemini_api_key: str = ""
    newsapi_api_key: str = ""
    finnhub_api_key: str = ""
    news_use_gemini_sentiment: bool = True
    firebase_project_id: str = ""
    firebase_service_account_path: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
