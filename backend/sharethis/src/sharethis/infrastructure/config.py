import os
from typing import Optional


class ImproperlyConfigured(Exception):
    pass


def get_env_var(name, default=None) -> Optional[str]:
    if not (var := os.environ.get(name, default)) and default is None:
        raise ImproperlyConfigured(f'No required variable: {name}')
    return var


class Config:
    WEB_APP_DOMAIN = get_env_var('WEB_APP_DOMAIN', 'https://www.demo.sharethis.space')

    DB_CONNECTION_STRING = get_env_var('DB_CONNECTION_STRING')

    OBJECT_STORAGE_PROVIDER = get_env_var('OBJECT_STORAGE_PROVIDER')
    OBJECT_STORAGE_ACCESSIBLE_URL = os.environ.get('OBJECT_STORAGE_ACCESSIBLE_URL')

    match OBJECT_STORAGE_PROVIDER:
        case 'AZURE':
            AZURE_CONNECTION_STRING = get_env_var('AZURE_CONNECTION_STRING')
            AZURE_BLOB_NAME = get_env_var('AZURE_BLOB_NAME')
        case 'AWS':
            AWS_BUCKET_URL = get_env_var('AWS_BUCKET_URL')
            AWS_ACCESS_KEY = get_env_var('AWS_ACCESS_KEY')
            AWS_SECRET_KEY = get_env_var('AWS_SECRET_KEY')
            AWS_BUCKET_NAME = get_env_var('AWS_BUCKET_NAME')
        case _:
            raise ImproperlyConfigured(
                f'Invalid OBJECT_STORAGE_PROVIDER ({OBJECT_STORAGE_PROVIDER}).'
                f'Valid options are: AZURE, AWS.'
            )

    MAIL_SERVICE = get_env_var('MAIL_SERVICE', 'mock')

    DEBUG = get_env_var('DEBUG', False) == 'True'


current_config = Config
