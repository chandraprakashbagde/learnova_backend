from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str 
    ALGORITHM: str

    RESEND_API_KEY: str
    
    BREVO_API_KEY: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str = "Learnova"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

setting = Setting()