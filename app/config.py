from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mistral_api_key: str = ""
    mistral_model: str = "mistral-14b-latest"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    mock_llm: bool = False

    ci4_whoami_url: str = ""
    ci4_timeout_seconds: float = 5.0

    allowed_origins: str = "http://localhost:8000"
    audit_log_path: str = "logs/ai_interactions.jsonl"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
