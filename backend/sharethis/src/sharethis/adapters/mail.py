import logging
from abc import ABC, abstractmethod

import requests

from sharethis.infrastructure.config import current_config


class IMailServiceInterface(ABC):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self._logger = logger

    @abstractmethod
    def send_new_upload_mail(self, url, email: str):
        raise NotImplementedError


class MailServiceMock(IMailServiceInterface):
    def send_new_upload_mail(self, url, email: str):
        self._logger.debug(f'{url} to {email}')
        self._logger.info('[mock] New upload mail sent successfully.')


class MailService(IMailServiceInterface):
    def send_new_upload_mail(self, url, email: str):
        self._logger.debug(f'{url} to {email}')
        try:
            response = requests.post(
                current_config.MAIL_SERVICE,
                json={'url': url, 'email': email, 'template': 'new_upload'},
                timeout=2
            )
            self._logger.info('New upload mail sent successfully.')
            self._logger.debug(response.text)
        except requests.exceptions.ConnectionError as e:
            self._logger.critical(str(e))
            self._logger.critical('Could not send mail.')
        else:
            if response.status_code not in [200, 201, 202]:
                self._logger.critical(f'Could not send email.: {response.status_code}')
                self._logger.debug(response.text)


def get_mail_service(mode=current_config.MAIL_SERVICE):
    if not mode or mode == 'mock':
        return MailServiceMock()
    return MailService()
