import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Iterable, Optional

from azure.core.exceptions import ResourceExistsError, AzureError
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    ContentSettings,
    generate_blob_sas,
    BlobSasPermissions, PartialBatchErrorException,
)
import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, BotoCoreError

from werkzeug.datastructures import FileStorage


class BucketStorageError(Exception):
    pass


class IBucketStorageClient(ABC):

    @abstractmethod
    def upload(self, key: str, file: FileStorage):
        raise NotImplementedError

    @abstractmethod
    def generate_temporary_access_link(
        self,
        key: str,
        content_type: str = None,
        content_disposition: str = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def bulk_delete(self, to_delete: Iterable):
        raise NotImplementedError


class AWSS3Client(IBucketStorageClient):
    def __init__(
        self,
        url,
        access_key,
        secret_key,
        bucket_name,
        logger: logging.Logger = logging.getLogger(__name__)
    ):
        self._client: BaseClient = boto3.client(
            service_name='s3',
            endpoint_url=url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._logger = logger
        self._bucket_name = bucket_name
        self.create_bucket()

    def create_bucket(self, bucket_name: str = None):
        try:
            self._client.create_bucket(Bucket=bucket_name or self._bucket_name)
        except ClientError:
            self._logger.debug('Container already exists. Continue process.')

    def upload(self, key: str, file: FileStorage):
        try:
            self._client.upload_fileobj(Fileobj=file, Bucket=self._bucket_name, Key=key)
        except BotoCoreError as e:
            self._logger.warning('AWSS3Client encountered an error during file upload.')
            self._logger.exception(e)
            raise BucketStorageError('Upload error.')

    def generate_temporary_access_link(
        self, key: str, content_type: str = None, content_disposition: str = None
    ):
        try:
            return self._client.generate_presigned_url(
                ClientMethod='get_object',
                ExpiresIn=timedelta(minutes=2).seconds,
                Params={
                    'Bucket': self._bucket_name,
                    'Key': key,
                    'ResponseContentDisposition': content_disposition,
                    'ResponseContentType': content_type,
                }
            )
        except BotoCoreError as e:
            self._logger.warning(
                'AWSS3Client encountered an error during presigned url creation.'
            )
            self._logger.exception(e)
            raise BucketStorageError('Presigned url creation error.')

    def bulk_delete(self, to_delete: Iterable):
        try:
            self._client.delete_objects(
                Bucket=self._bucket_name,
                Delete={
                    'Objects': [{'Key': key} for key in to_delete],
                    'Quiet': False,
                }
            )
        except BotoCoreError as e:
            self._logger.warning('AWSS3Client encountered an error during bulk file delete.')
            self._logger.exception(e)
            raise BucketStorageError('Delete error.')


class AzureBlobClient(IBucketStorageClient):
    def __init__(
        self,
        connection_string,
        container_name,
        logger: logging.Logger = logging.getLogger(__name__)
    ):
        self._logger = logger
        self._connection_string: str = connection_string
        self._container_name: str = container_name
        self._container_client: Optional[ContainerClient] = None
        self._blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(
            self._connection_string
        )
        self.create_container()

    def create_container(self, container_name: str = None):
        try:
            self._container_client = self._blob_service_client.create_container(
                container_name or self._container_name
            )
        except ResourceExistsError:
            self._logger.debug('Container already exists. Continue process.')

    def upload(self, key: str, file: FileStorage):
        try:
            blob_client: BlobClient = self._blob_service_client.get_blob_client(
                container=self._container_name,
                blob=key
            )
            blob_client.upload_blob(
                file.read(),
                content_settings=ContentSettings(content_type=file.content_type)
            )
        # Catch any Azure error because we don't need any specific error for now.
        # We want to map client specific errors into internal errors.
        except AzureError as e:
            self._logger.warning('AzureBlobClient encountered an error during blob upload.')
            self._logger.exception(e)
            raise BucketStorageError('Upload error.')

    def generate_temporary_access_link(
        self, key: str, content_type: str = None, content_disposition: str = None
    ):
        sas = generate_blob_sas(
            account_name=self._blob_service_client.account_name,
            account_key=self._blob_service_client.credential.account_key,

            container_name=self._container_name,
            blob_name=key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=2),
            content_type=content_type,
            content_disposition=content_disposition,
        )
        return 'https://{}.blob.core.windows.net/{}/{}?{}'.format(
            self._blob_service_client.account_name, self._container_name, key, sas
        )

    def bulk_delete(self, to_delete: Iterable):
        container_client = self._blob_service_client.get_container_client(self._container_name)
        try:
            result = container_client.delete_blobs(*to_delete)
            self._logger.debug(result)
        except PartialBatchErrorException as e:
            self._logger.warning('AzureBlobClient encountered an error during bulk blob delete.')
            self._logger.exception(e)
            raise BucketStorageError('Delete error.')
