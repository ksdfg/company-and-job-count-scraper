from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LI_AT_COOKIE: str


settings = Settings()
