from sharethis.entrypoints import api

# Gunicorn is looking for application, and we want to keep it default.
application = api.app
