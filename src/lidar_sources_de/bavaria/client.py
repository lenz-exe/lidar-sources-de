import os
from typing import Optional

import requests

from lidar_sources_de.bavaria.kml_parser import parse_regions_kml
from lidar_sources_de.bavaria.meta4_parser import parse_meta4_file
from lidar_sources_de.bavaria.models import PortalBavariaMeta4, PortalBavariaRegionsKml


class PortalBavariaClient:
    def __init__(self, timeout: int = 15, debug: bool = False) -> None:
        """

        :param timeout: An int (seconds) how long to wait for a response
        :param debug: Bool: Activates debug mode for more printing
        """
        self.timeout = timeout
        self.debug = debug

    def load_regions_from_kml(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
    ) -> list[PortalBavariaRegionsKml]:
        """
        Method to convert kml file from GeoPortal Bavaria into usefully dataclasses.

        :param path: Optional path to a local kml file
        :param url: Optional url to a kml file
        :return: a list of PortalBavariaRegionsKml objects
        """
        if path:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File {path} does not exist")
            with open(path, "rb", encoding="utf-8") as file:
                content = file.read()
        elif url:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            content = resp.content
        else:
            raise ValueError("Either path or url must be provided")
        return parse_regions_kml(content)

    def load_tiles(self, regions: list[PortalBavariaRegionsKml]) -> list[PortalBavariaMeta4]:
        """
        Method to get single tiles out of a meta4 file by looping through the regions
        list of PortalBavariaRegionsKml objects.
        :param regions: A list of PortalBavariaRegionsKml objects
        :return: A list of PortalBavariaMeta4 objects
        """
        return parse_meta4_file(regions, timeout=self.timeout, debug=self.debug)
