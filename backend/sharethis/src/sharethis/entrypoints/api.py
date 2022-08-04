import logging
from dataclasses import asdict

from flask import request
from flask_cors import CORS

from sharethis.infrastructure.config import current_config
from sharethis.infrastructure.main import (
    app, db
)
from sharethis.infrastructure.schemas import UploadSchema
from sharethis.logic.dtos import UploadResultDTO, UploadDTO
from sharethis.logic.use_cases import UploadUseCase, DownloadUseCase


cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.teardown_appcontext
def shutdown_session(exception: Exception = None) -> None:
    db.get_session().close()


@app.route('/api/upload', methods=['POST'])
def upload():
    request_data: dict = UploadSchema().load({**request.files, **request.form})
    result: UploadResultDTO = UploadUseCase().upload(
        file=request_data['file'],
        upload_dto=UploadDTO(**request_data['data'])
    )
    return asdict(result)


@app.route('/api/download/<string:key>', methods=['GET'])
def download(key: str):
    return asdict(DownloadUseCase().download(key))


@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    app.run(debug=current_config.DEBUG, host='0.0.0.0', port=8080)
