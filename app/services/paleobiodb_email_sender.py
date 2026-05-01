import smtplib
import ssl
import logging
from pathlib import Path
from typing import List

from email.message import EmailMessage

from app.services.paleobiodb_dataset import PaleobiodbDataset

logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """
    Raised when there is an issue during sending email preparation or sending.
    """
    pass


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
        """
        Validates parameters for sending email preparation or sending.

        :raises EmailSendError: If there are missing required parameters.
        """
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
            raise EmailSendError(f"Missing required parameters: {missing_params}")

    def send_email_report(self, subject: str, dataset: PaleobiodbDataset, data_file: Path) -> None:
        """
        Sends an email report to the specified recipients.

        :param subject: Subject line of the email.
        :param dataset: PaleoBioDB dataset.
        :param data_file: CSV file containing PaleobioDB records to be included in the email body as attachment.
        :raises EmailSendError: If the email cannot be sent due to SMTP errors or connection issues.
        """

        if not self.enable:
            return

        if not dataset.records:
            logger.warning("PaleoBioDB dataset is empty - skipping sending email report.")
            return

        email = EmailMessage()
        email['From'] = self.mail_from
        email['To'] = ", ".join(self.mail_to)
        email['Subject'] = subject

        email.set_content("Found occurrences can be found in attachment.")
        with data_file.open(mode="rb") as file:

            email.add_attachment(file.read(),
                       maintype="text",
                       subtype="csv",
                       filename=data_file.name)

        context = ssl.create_default_context()

        logger.debug("Sending message...")
        try:
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as smtp:
                smtp.login(self.login, self.password)
                smtp.send_message(email)
        except smtplib.SMTPException as smtp_exc:
            raise EmailSendError(f"Error during sending email message") from smtp_exc

        logger.debug("Message has been sent.")
