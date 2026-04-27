from pydantic_settings import BaseSettings


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

    # Anthropic Claude API (retained for the TikTok marketing script generator)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"

    # GDPR retention — strip api_calls.response_body + error after this many days.
    # Keeps the row itself (service, endpoint, status, duration, cost) so cost
    # rollups stay intact.
    API_CALL_RESPONSE_RETENTION_DAYS: int = 30

    # One Auto API (Experian + Brego via single integration)
    ONEAUTO_API_KEY: str = ""
    ONEAUTO_API_URL: str = "https://sandbox.oneautoapi.com"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    # Flip on once Stripe Dashboard → Settings → Public details has a Terms
    # of service URL set. Without that URL, Stripe rejects checkout creation
    # with HTTP 400 if consent_collection is configured. Default off so a
    # missing dashboard setting can never block payments.
    STRIPE_TOS_CONSENT_ENABLED: bool = False

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "matthew@vericar.co.uk"

    # Site URL (frontend base URL for Stripe redirects etc.)
    SITE_URL: str = "http://localhost:3001"

    # Gumtree Scraping
    GUMTREE_TIMEOUT: float = 20.0
    GUMTREE_REQUEST_DELAY: float = 1.5
    GUMTREE_CACHE_TTL: int = 1800
    GUMTREE_USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    # CORS (comma-separated string, parsed in main.py)
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_BURST: int = 10

    # Monitoring
    SENTRY_DSN: str = ""

    # Admin endpoints — re-send emails, view recent fulfilments etc.
    # Set to a long random string in Railway. Empty disables admin endpoints.
    ADMIN_API_TOKEN: str = ""

    # Discord webhook for critical operational alerts (email failures,
    # new payments, etc). Empty disables all Discord notifications.
    # GDPR: never send PII like customer emails or names — only operational
    # identifiers (registration, session_id, report_ref, tier).
    DISCORD_WEBHOOK_URL: str = ""

    # PostHog server-side analytics (in addition to client-side via
    # frontend/src/lib/analytics.ts). Empty disables all backend events.
    # Use the same project key as the frontend so events land in one project.
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://eu.i.posthog.com"
    # Server-side pepper used to hash registration plates before they're
    # passed to PostHog as a distinct_id. Not a real secret (PostHog has
    # them anyway), but rotating it would force a new identity space.
    POSTHOG_REG_HASH_PEPPER: str = "vericar-default-pepper-set-in-prod"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # tolerate frontend NEXT_PUBLIC_* keys in shared .env


settings = Settings()
