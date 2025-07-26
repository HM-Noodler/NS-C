# app/config.py
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_name: str = Field(..., env="DB_NAME")
    db_connection_name: str = Field(..., env="DB_CONNECTION_NAME")
    
    # Application
    environment: str = Field("local", env="ENVIRONMENT")
    project_name: str = Field("FastAPI Template", env="PROJECT_NAME")
    version: str = Field("1.0.0", env="VERSION")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    
    # External Services (kept for reference)
    # Stytch Authentication
    stytch_api_url: str = Field("https://api.stytch.com/v1", env="STYTCH_API_URL")
    stytch_tier_2_project_id: Optional[str] = Field(None, env="STYTCH_TIER_2_PROJECT_ID")
    stytch_tier_2_secret: Optional[str] = Field(None, env="STYTCH_TIER_2_SECRET")
    stytch_tier_3_project_id: Optional[str] = Field(None, env="STYTCH_TIER_3_PROJECT_ID")
    stytch_tier_3_secret: Optional[str] = Field(None, env="STYTCH_TIER_3_SECRET")
    
    # SMTP Configuration
    smtp_host: Optional[str] = Field(None, env="SMTP_HOST")
    smtp_port: Optional[str] = Field(None, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    from_email: Optional[str] = Field(None, env="FROM_EMAIL")
    from_name: Optional[str] = Field(None, env="FROM_NAME")
    
    # AI Configuration
    claude_api_key: Optional[str] = Field(None, env="CLAUDE_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()
