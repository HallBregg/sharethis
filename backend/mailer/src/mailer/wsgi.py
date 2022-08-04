from mailer.main import app


# Gunicorn is looking for application, and we want to keep it default.
application = app
