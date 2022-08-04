import logging
import logging.config

from flask import Flask

from sharethis.adapters.bucket import AzureBlobClient, AWSS3Client
from sharethis.infrastructure.config import current_config
from sharethis.infrastructure.db import SQLAlchemyDatabase
from sharethis.infrastructure.exceptions import handlers_controller


def config_logger():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '%(asctime)s [%(processName)s] [%(threadName)s] | %(module)s | %(filename)s | %(funcName)s | [%(name)s] [%(levelname)s]  %(message)s'  # noqa
                },
            'colored_small': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '%(asctime)s | %(funcName)s | %(message)s'
                },
        },
        'handlers': {
            'console': {
                'formatter': 'colored',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'level': 'DEBUG'
            },
        },
        'loggers': {
            'flask_cors': {
                'handlers': ['console'],
                'level': logging.DEBUG if current_config.DEBUG else logging.INFO,
                'propagate': True,
            },
            'gunicorn': {
                'handlers': ['console'],
                'level': logging.DEBUG if current_config.DEBUG else logging.INFO,
                'propagate': True
            },
            'sharethis': {
                'handlers': ['console'],
                'level': logging.DEBUG if current_config.DEBUG else logging.INFO,
                'propagate': True
            },
        }
    })
    logger = logging.getLogger(__name__)
    return logger


def get_logger():
    return logging.getLogger(__name__)


def get_bucket_storage_client():
    match current_config.OBJECT_STORAGE_PROVIDER:
        case 'AZURE':
            return AzureBlobClient(
                connection_string=current_config.AZURE_CONNECTION_STRING,
                container_name=current_config.AZURE_BLOB_NAME,
            )
        case 'AWS':
            return AWSS3Client(
                url=current_config.AWS_BUCKET_URL,
                access_key=current_config.AWS_ACCESS_KEY,
                secret_key=current_config.AWS_SECRET_KEY,
                bucket_name=current_config.AWS_BUCKET_NAME,
            )


def create_app():
    config_logger()
    app = Flask(__name__)
    handlers_controller.initialize(app)
    app.config.from_object(current_config)

    db = SQLAlchemyDatabase(current_config.DB_CONNECTION_STRING)
    db.create_database()

    bucket_storage_client = get_bucket_storage_client()

    return app, db, bucket_storage_client


app, db, bucket_storage_client = create_app()
