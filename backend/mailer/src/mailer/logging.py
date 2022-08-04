import logging
import logging.config

from mailer.config import DEBUG


def config_logger():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': '%(asctime)s [%(processName)s] [%(threadName)s] | %(module)s | %(filename)s | %(funcName)s | [%(name)s] [%(levelname)s]  %(message)s'
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
            '': {'handlers': ['console'], 'level': logging.DEBUG if DEBUG else logging.INFO, 'propagate': True},
            'sharethis': {'handlers': ['console'], 'level': logging.DEBUG if DEBUG else logging.INFO, 'propagate': False},
        }
    })
