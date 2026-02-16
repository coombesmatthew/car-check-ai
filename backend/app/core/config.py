from pydantic import field_validator
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

    # DVSA MOT History API (new OAuth 2.0 API)
    MOT_API_KEY: str = ""
    MOT_CLIENT_ID: str = ""
    MOT_CLIENT_SECRET: str = ""
    MOT_TOKEN_URL: str = "https://login.microsoftonline.com/a455b827-244f-4c97-b5b4-ce5d13b4d00c/oauth2/v2.0/token"
    MOT_SCOPE_URL: str = "https://tapi.dvsa.gov.uk/.default"
    MOT_API_URL: str = "https://history.mot.api.gov.uk/v1/trade/vehicles/registration"

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
    FROM_EMAIL: str = "reports@vericar.co.uk"

    # Site URL (frontend base URL for Stripe redirects etc.)
    SITE_URL: str = "http://localhost:3001"

    # Gumtree Scraping
    GUMTREE_TIMEOUT: float = 20.0
    GUMTREE_REQUEST_DELAY: float = 1.5
    GUMTREE_CACHE_TTL: int = 1800
    GUMTREE_USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated strings (e.g. from Railway env vars)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_BURST: int = 10

    # Monitoring
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
