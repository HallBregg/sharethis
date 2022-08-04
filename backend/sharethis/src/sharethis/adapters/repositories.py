import datetime
import logging
from abc import ABC

from werkzeug.datastructures import FileStorage

from sharethis.adapters.bucket import IBucketStorageClient
from sharethis.infrastructure.models import ContentMeta


class RepositoryException(Exception):
    pass


class EntityDoesNotExist(RepositoryException):
    pass


class IRepository(ABC):
    def __init__(
        self,
        logger: logging.Logger = logging.getLogger(__name__)
    ):
        self._logger = logger


class IBucketStorageRepository(IRepository):
    def __init__(self, client: IBucketStorageClient, *args, **kwargs):
        self._client = client
        super().__init__(*args, **kwargs)


class ISQLAlchemyRepository(IRepository):
    def __init__(self, session, *args, **kwargs):
        self._session = session
        super().__init__(*args, **kwargs)


class ContentRepository(IBucketStorageRepository):
    def upload(self, key, file: FileStorage):
        self._client.upload(key, file)

    def bulk_delete(self, to_delete):
        if to_delete:
            self._client.bulk_delete(to_delete)

    def presigned_download_link(self, key, content_type, file_name):
        return self._client.generate_temporary_access_link(
            key, content_type, f'attachment; filename={file_name}'
        )


class ContentMetaRepository(ISQLAlchemyRepository):
    def add(self, instance: ContentMeta):
        self._session.add(instance)

    def delete_by_key(self, key):
        self._session.query(ContentMeta).filter(ContentMeta.key == key).delete()

    def delete_expired(self):
        records_to_delete = self._session.query(ContentMeta).filter(
            ContentMeta.expiration_date <= datetime.datetime.now()
        )
        keys_to_delete = list(
            map(lambda instance: getattr(instance, 'key'), records_to_delete.all())
        )
        records_to_delete.delete()
        return keys_to_delete

    def retrieve_non_expired_by_key(self, key):
        """
        Raises:
            sqlalchemy.exc.MultipleResultsFound
            sqlalchemy.exc.NoResultFound
        """
        return self._session.query(ContentMeta).filter(
            ContentMeta.key == key,
            ContentMeta.expiration_date > datetime.datetime.now()
        ).one()
