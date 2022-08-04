import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

from marshmallow import Schema

from mailer.config import MODE, SMTP_SERVER, SMTP_PORT, SMTP_PASSWORD, SMTP_LOGIN, SENDER_EMAIL
from mailer.exceptions import NoHandlerForTemplate
from mailer.schemas import NewUploadSchema, UploadDownloadedSchema


class Mail:
    schema: Type[Schema] = NotImplementedError
    name: str = NotImplementedError

    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self._logger = logger

    def template(self, *args, **kwargs):
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        raise NotImplementedError

    def send(self, recipients, message):
        if MODE == 'SSL':
            with smtplib.SMTP_SSL(
                    SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()
            ) as server:
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipients, message)
        elif MODE == 'TLS':
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipients, message)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(context=ssl.create_default_context())
                server.sendmail(SENDER_EMAIL, recipients, message)


class NewUpload(Mail):
    schema = NewUploadSchema
    name = 'new_upload'

    def handle(self, data):
        self._logger.debug('Handle')
        cleaned_data = self.schema().load(data)
        email = cleaned_data.pop('email')
        message = self.template(**cleaned_data)
        self._logger.debug(f'email: {email}')
        self._logger.debug(f'message: {message}')

        try:
            self.send([email], message)
        except Exception as e:
            self._logger.debug(e)
            return False
        return True

    def template(self, url):
        message = MIMEMultipart()
        message['Subject'] = 'New Sharethis upload'
        message.attach(MIMEText(
            'Hello from Sharethis.\n'
            f'New Sharethis upload is available.\n'
            f'You can download it here: {url}',
            'plain'
        ))
        return message.as_string()


class MailCollector:
    def __init__(
        self,
        mail_handlers: list[Type[Mail]],
        logger: logging.Logger = logging.getLogger(__name__)
    ):
        self._mail_handlers = mail_handlers
        self._logger = logger
        self._mapper = {}
        self.propagate_mail_handlers()

    def propagate_mail_handlers(self):
        for mail in self._mail_handlers:
            self._mapper[mail.name] = mail()

    def get_handler(self, template):
        try:
            return self._mapper[template]
        except KeyError:
            raise NoHandlerForTemplate
