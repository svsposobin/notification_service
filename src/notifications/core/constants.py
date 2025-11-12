from os import getenv

from src.notifications.core.schemas import SessionPool, GmailEnvironments

DEFAULT_POOL_SETTNGS: SessionPool = SessionPool(  # Ignoring types for pydantic auto-serialization
    limit=getenv("POOL_LIMIT", ""),  # type: ignore
    limit_per_host=getenv("POOL_LIMIT_PER_HOST", ""),  # type: ignore
    keepalive_timeout=getenv("POOL_KEEPALIVE_TIMEOUT", ""),  # type: ignore
    ssl=getenv("POOL_SSL", "")  # type: ignore
)

DEFAULT_GMAIL_NOTIF_ENVIRONMENTS: GmailEnvironments = GmailEnvironments(
    gmail_address=getenv("GMAIL_ADDRESS", ""),
    gmail_app_password=getenv("GMAIL_APP_PASSWORD", "")
)
