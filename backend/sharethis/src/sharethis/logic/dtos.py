from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


@dataclass
class UploadDTO:
    time_to_live: timedelta
    encryption_method: str
    email: Optional[str] = None


@dataclass(frozen=True)
class UploadResultDTO:
    key: str


@dataclass(frozen=True)
class DownloadResultDTO:
    url: str
    encryption_method: str
    file_name: str
