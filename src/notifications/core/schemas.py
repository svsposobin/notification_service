from typing import Any, Optional

from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv(".env.test"))


class SessionPool(BaseModel):
    limit: int
    limit_per_host: int
    keepalive_timeout: int
    ssl: bool


class GmailEnvironments(BaseModel):
    gmail_address: str
    gmail_app_password: str


class BaseResponse(BaseModel):
    status_code: Optional[int] = None
    details: Optional[Any] = None
    execute_status: bool = False  # For audit
