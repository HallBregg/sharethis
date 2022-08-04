import logging

from flask import Flask, request

from mailer.exceptions import (
    ExceptionHandlerMapper,
    BadRequest,
    NotFound,
    CoreHttpError,
    NoHandlerForTemplate
)
from mailer.logging import config_logger
from mailer.mails import MailCollector, NewUpload


config_logger()
app = Flask(__name__)
ExceptionHandlerMapper(app)


logger = logging.getLogger(__name__)


@app.route('/send', methods=['POST'])
def send_view():
    if not (data := request.json):
        raise BadRequest
    if not (template := data.pop('template')):
        raise BadRequest(details={'template': 'This field is required.'})
    try:
        handler = mc.get_handler(template)
        logger.debug(handler)
    except NoHandlerForTemplate:
        raise BadRequest('Given template does not exist.')
    if not handler.handle(data):
        raise CoreHttpError(message='Mail server is unavailable.')
    logger.debug('Send')
    return {'success': True, 'message': 'Email send successfully.'}, 200


if __name__ == '__main__':
    mc = MailCollector(mail_handlers=[NewUpload])
    app.run(host='0.0.0.0', port=8080, debug=True)
