from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "Car Check AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600
    REDIS_DVLA_TTL: int = 86400  # 24 hours - DVLA data changes infrequently
    REDIS_MOT_TTL: int = 3600  # 1 hour - MOT data updated daily

    # DVSA MOT History API
    MOT_API_KEY: str = ""
    MOT_API_URL: str = "https://beta.check-mot.service.gov.uk/trade/vehicles/mot-tests"

    # DVLA Vehicle Enquiry Service API
    DVLA_VES_API_KEY: str = ""
    DVLA_VES_URL: str = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"

    # Brego Valuations (Basic+ tier)
    BREGO_API_KEY: str = ""
    BREGO_API_URL: str = ""

    # Percayso/Cazana Valuations (Premium tier)
    PERCAYSO_API_KEY: str = ""
    PERCAYSO_API_URL: str = ""

    # Experian AutoCheck (Premium tier)
    EXPERIAN_API_KEY: str = ""
    EXPERIAN_API_URL: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "reports@carcheck.ai"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Monitoring
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
