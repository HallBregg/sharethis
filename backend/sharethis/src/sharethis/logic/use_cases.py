import mimetypes
import uuid
from datetime import datetime
from typing import Optional

import urllib

from sharethis.adapters.mail import get_mail_service
from sharethis.infrastructure.config import current_config
from sharethis.infrastructure.main import db, bucket_storage_client
from sharethis.infrastructure.models import ContentMeta
from sharethis.logic.dtos import UploadDTO, UploadResultDTO, DownloadResultDTO
from sharethis.services.uow import MainUnitOfWork


class UploadUseCase:

    @staticmethod
    def generate_unique_key() -> str:
        return str(uuid.uuid4().hex)

    def send_new_upload_email(self, key: str, send_to: Optional[str] = None):
        if not send_to:
            return
        get_mail_service().send_new_upload_mail(
            url=f"{current_config.WEB_APP_DOMAIN}/key/{key}",
            email=send_to,
        )

    def upload(self, file, upload_dto: UploadDTO) -> UploadResultDTO:
        unique_key_for_upload = self.generate_unique_key()

        # Create instance of ContentMeta.
        cm = ContentMeta(
            key=unique_key_for_upload,
            name=file.filename,
            content_type=file.content_type or mimetypes.guess_type(file.filename),
            expiration_date=datetime.now() + upload_dto.time_to_live,
            encryption_method=upload_dto.encryption_method,
        )

        # Execute logic.
        with MainUnitOfWork(db, bucket_storage_client) as uow:
            uow.content_meta.add(cm)
            uow.content.upload(unique_key_for_upload, file)
            uow.commit()

        # Send email about new upload.
        self.send_new_upload_email(unique_key_for_upload, upload_dto.email)

        return UploadResultDTO(key=unique_key_for_upload)


class DownloadUseCase:
    @staticmethod
    def format_download_url(original: str, accessible_url: Optional[str] = None) -> str:
        # Access to a protected member _replace of a class.
        # We need this in order to access undocumented part of urllib.
        if not accessible_url:
            return original
        base = urllib.parse.urlparse(original)
        new = urllib.parse.urlparse(accessible_url)
        overwritten = base._replace(scheme=new.scheme, netloc=new.netloc)
        return overwritten.geturl()

    def download(self, key: str) -> DownloadResultDTO:
        with MainUnitOfWork(db, bucket_storage_client) as uow:
            cm = uow.content_meta.retrieve_non_expired_by_key(key)
            presigned_url = uow.content.presigned_download_link(cm.key, cm.content_type, cm.name)
        return DownloadResultDTO(
            url=self.format_download_url(
                presigned_url, current_config.OBJECT_STORAGE_ACCESSIBLE_URL
            ),
            encryption_method=cm.encryption_method,
            file_name=cm.name,
        )
