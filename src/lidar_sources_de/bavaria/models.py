from dataclasses import dataclass


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
    hash_type: str
    hash_value: str


@dataclass
class KmlItemDescription:
    name: str
    area_km2: float
    file_count: int
    download_size: str
    download_size_mb: float
    metalink: str
