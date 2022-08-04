from abc import ABC, abstractmethod
import logging

from sharethis.infrastructure.db import SQLAlchemyDatabase

from sharethis.adapters.bucket import IBucketStorageClient
from sqlalchemy.orm import Session, scoped_session

from sharethis.adapters.repositories import ContentRepository, ContentMetaRepository


class IUnitOfWork(ABC):
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        self._logger = logger

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, type, value, traceback):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    # All repositories should be implemented as a property
    # eg:
    #       @property
    #       @abstractmethod
    #       def repo1(self):
    #           return Repository1()


class MainUnitOfWork(IUnitOfWork):
    def __init__(
        self, db_client: SQLAlchemyDatabase, bucket_storage_client: IBucketStorageClient, *args, **kwargs
    ):
        self._db_client = db_client
        self._bucket_storage_client = bucket_storage_client
        super().__init__(*args, **kwargs)

    def __enter__(self):
        self._session: Session = self._db_client.get_session()
        return self

    def __exit__(self, type, value, traceback):
        self._logger.debug(f'UOW exit | type: {type}, value: {value}, traceback: {traceback}')
        if type:
            self.rollback()
        else:
            self._close()

    def rollback(self):
        self._session.rollback()
        self._logger.debug('UOW rollback')

    def commit(self):
        self._session.commit()
        self._logger.debug('UOW commit')

    def _close(self):
        self._session.close()
        self._logger.debug('UOW close')

    @property
    def content(self) -> ContentRepository:
        return ContentRepository(self._bucket_storage_client)

    @property
    def content_meta(self) -> ContentMetaRepository:
        return ContentMetaRepository(self._session)
