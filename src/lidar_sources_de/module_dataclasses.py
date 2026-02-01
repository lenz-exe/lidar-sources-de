from dataclasses import dataclass
from typing import Optional


@dataclass
class PortalBavariaRegionsKml:
    placemark_name: str
    placemark_file_count: int
    placemark_download_size: str
    placemark_download_size_mb: float
    placemark_metalink: str
    placemark_area_km2: float


@dataclass
class PortalBavariaMeta4:
    file_name: str
    file_size: int
    download_url: str
    hash_type: Optional[str] = None
    hash_value: Optional[str] = None
