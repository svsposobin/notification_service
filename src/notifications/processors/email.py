import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from aiosmtplib import SMTP as AIO_SMTP
from aiosmtplib.errors import (
    SMTPServerDisconnected,
    SMTPTimeoutError,
    SMTPConnectError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
    SMTPAuthenticationError
)

from src.notifications.core.interface import NotificationInterface
from src.notifications.core.constants import DEFAULT_GMAIL_NOTIF_ENVIRONMENTS
from src.notifications.core.schemas import BaseResponse


class GmailNotificationProcessor(NotificationInterface):
    """
    Asynchronous Gmail SMTP email sender with connection reuse and retry logic.

    For high-throughput scenarios, consider wrapping this class with a connection pool
    (e.g., using asyncio.Queue + worker tasks) to parallelize email sending.

    Example pool implementation available upon request.
    """

    def __init__(
            self,
            gmail_address: str = DEFAULT_GMAIL_NOTIF_ENVIRONMENTS.gmail_address,
            gmail_app_password: str = DEFAULT_GMAIL_NOTIF_ENVIRONMENTS.gmail_app_password,
            smtp_gmail_hostname: str = "smtp.gmail.com",
            smtp_gmail_port: int = 587,
            smtp_gmail_start_tls: bool = True
    ) -> None:
        """
        Initializes the Gmail SMTP notification client.

        If necessary, external pooling (e.g., via asyncio.Queue + workers) can be implemented
        to handle high-throughput email sending.

        Args:
            gmail_address (str): Sender email address (e.g., "you@gmail.com").
            gmail_app_password (str): Gmail App Password generated in Google Account settings.
            smtp_gmail_hostname (str): SMTP server hostname (default: "smtp.gmail.com").
            smtp_gmail_port (int): SMTP server port (default: 587).
            smtp_gmail_start_tls (bool): Whether to use STARTTLS (default: True).
        """
        # Gmail environments:
        self._gmail_address = gmail_address
        self.__gmail_app_password = gmail_app_password
        # SMTP environments:
        self._smtp_gmail_hostname = smtp_gmail_hostname
        self._smtp_gmail_port = smtp_gmail_port
        self._smtp_gmail_start_tls = smtp_gmail_start_tls
        # SMTP client:
        self._smtp_client: Optional[AIO_SMTP] = None

    async def send(
            self,
            to_email: str,
            subject: str,
            text: str,
            max_retries: int = 3,
    ) -> BaseResponse:
        """
        Sends an email via Gmail SMTP with retry logic for transient errors.

        Args:
            to_email (str): Recipient email address.
            subject (str): Email subject line.
            text (str): Plain-text body of the email.
            max_retries (int): Maximum number of retry attempts for temporary failures (default: 3).

        Returns:
            BaseResponse: Object containing status_code, details, and execute_status.

        Note:
            Retries only occur for temporary network/SMTP errors (e.g., timeout, disconnect).
            Permanent errors (e.g., auth failure, invalid recipient) fail immediately.
        """
        result: BaseResponse = BaseResponse()

        msg: MIMEMultipart = MIMEMultipart()
        msg["From"] = self._gmail_address
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain", "utf-8"))

        for attempt in range(max_retries):
            try:
                await self._get_connection()  # Lazy initialization

                assert self._smtp_client is not None
                await self._smtp_client.send_message(msg)

                result.status_code = 200
                result.details = "The message was sent successfully"
                result.execute_status = True
                break

            except (SMTPServerDisconnected, SMTPTimeoutError, SMTPConnectError) as error:
                await self._reset_connection()
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

                else:
                    result.status_code = 500
                    result.details = str(error)

            except (SMTPRecipientsRefused, SMTPSenderRefused, SMTPAuthenticationError) as error:
                result.status_code = 400
                result.details = str(error)
                break

            except Exception as error:
                result.status_code = 500
                result.details = str(error)
                break

        return result

    async def _get_connection(self) -> None:
        """
        Ensures a live SMTP connection is available.

        If an existing connection exists, checks its liveness via NOOP command.
        If dead or absent, creates and authenticates a new connection.

        Raises:
            Any SMTP or network exception during connect/login (handled by caller).
        """
        if self._smtp_client:
            try:
                await self._smtp_client.noop()  # Checking the connection
                return

            except Exception:  # noqa
                await self._reset_connection()

        self._smtp_client = AIO_SMTP(
            hostname=self._smtp_gmail_hostname,
            port=self._smtp_gmail_port,
            start_tls=self._smtp_gmail_start_tls,
        )
        await self._smtp_client.connect()
        await self._smtp_client.login(
            self._gmail_address,
            self.__gmail_app_password,
        )

    async def _reset_connection(self) -> None:
        """
        Gracefully closes the current SMTP connection (if any) and resets the client reference.

        Safe to call even if no connection exists. Any errors during quit() are suppressed.
        """
        if self._smtp_client:
            try:
                await self._smtp_client.quit()

            except Exception:  # noqa
                pass

            self._smtp_client = None

    async def close_session(self):
        """
        Closes the SMTP connection gracefully.

        Intended for use in application lifespan handlers (e.g., FastAPI on_shutdown).
        Does not reset the client reference — call _reset_connection() if needed.
        """
        if self._smtp_client:
            await self._smtp_client.quit()  # noqa
