from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    DB_URL: str

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str
    JWT_ACTIVATION_EXPIRATION_SECONDS: int


settings = Settings()
