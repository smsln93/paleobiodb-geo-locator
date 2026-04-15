import smtplib
import ssl
import traceback
import logging
from typing import List

from email.message import EmailMessage


logger = logging.getLogger(__name__)


class PaleobiodbEmailSender:
    """
    Handles sending HTML email reports using an SMTP server.

    Attributes:
        host (str): SMTP server hostname.
        login (str): SMTP login username.
        mail_from (str): Email address that appears in the 'From' field.
        password (str): SMTP login password.
        port (int): SMTP server port.
        mail_to (List[str]): List of recipient email addresses.
    """
    def __init__(self, host: str, login: str, mail_from: str, password: str, port: int, mail_to: List[str]):
        self.host = host
        self.login = login
        self.mail_from = mail_from
        self.password = password
        self.port = port
        self.mail_to = mail_to if mail_to else []

        self.enable = bool(self.mail_to)
        if not self.enable:
            logger.warning("No recipients provided. Emails will not be sent.")
        else:
            self._validate_parameters()

    def _validate_parameters(self) -> None:
        missing_params: List = []

        if not self.host:
            missing_params.append("host")

        if not self.login:
            missing_params.append("login")

        if not self.mail_from:
            missing_params.append("mail_from")

        if not self.password:
            missing_params.append("password")

        if not self.port:
            missing_params.append("port")

        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")

    def send_html_report(self, subject: str, title: str, html_table: str) -> None:
        """
        Sends an HTML email report to the specified recipients.

        :param subject: Subject line of the email.
        :param title: Title of the report.
        :param html_table: HTML table containing PaleobioDB records configs to be included in the email body.
        :raises smtplib.SMTPException: If there is an issue related to SMTP during sending.
        :raises Exception: If there is any other issue during email preparation or sending.
        """

        logger.debug("Sending message...")

        html_content = f"""
        <html>
          <body>
            <p>{title}</p>
            {html_table}
          </body>
        </html>
        """

        if not self.enable:
            logger.info("Skipping sending HTML report.")
            return

        email = EmailMessage()
        email['From'] = self.mail_from
        email['To'] = ", ".join(self.mail_to)
        email['Subject'] = subject
        email.add_alternative(html_content, subtype="html")

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as smtp:
                smtp.login(self.login, self.password)
                smtp.sendmail(self.mail_from, self.mail_to, email.as_string())
        except smtplib.SMTPException as smtp_exc:
            logger.error(f"SMTP-related error during sending: {smtp_exc}")
        except Exception as exc:
            logger.error(f"Failed to send email: {exc}\n{traceback.format_exc()}")
        else:
            logger.debug("Message has been sent.")
