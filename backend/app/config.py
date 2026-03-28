from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = 3001
    jwt_secret: str = ""
    frontend_origin: str = "http://localhost:5173"
    # Never log or JSON-serialize this field; use .get_secret_value() only when calling OpenAI.
    openai_api_key: SecretStr = SecretStr("")
    # Default to lowest-cost chat model; override if your account returns "model not found"
    # (e.g. OPENAI_MODEL=gpt-4o-mini).
    openai_model: str = "gpt-5-nano"


settings = Settings()
