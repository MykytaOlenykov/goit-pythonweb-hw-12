from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    PORT: int = 8000
    HOST: str = "localhost"
    BASE_URL: str = "http://localhost:8000"
    DB_URL: str
    ECHO_SQL: bool = False
    CORS_ORIGINS: str = "*"

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str
    JWT_VERIFICATION_EXPIRATION_SECONDS: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str
    MAIL_PORT: int = 465


settings = Settings()
