import os

MODE = os.environ['MODE']
SMTP_SERVER = os.environ['SMTP_SERVER']
SMTP_PORT = os.environ['SMTP_PORT']
SMTP_LOGIN = os.environ['SMTP_LOGIN']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
SENDER_EMAIL = os.environ['SENDER_EMAIL']
DEBUG = os.environ.get('DEBUG', False) == 'True'
