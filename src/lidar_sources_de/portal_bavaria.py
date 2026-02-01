# kml file: https://services.atlas.bayern.de/proxy/?url=https%3A%2F%2Fgeodaten.bayern.de%2Fodd%2Fa%2Flaser%2Fmeta%2Fkml%2Fgemeinde.kml
import json
import os
from typing import Optional
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from lidar_sources_de.module_dataclasses import PortalBavariaMeta4, PortalBavariaRegionsKml
from lidar_sources_de.module_utils import check_if_url_exists, unescape_html, write_data_to_file

KmlRegionsDescriptionTranslation = {
    "Gebiet": "name",
    "Fläche": "area_km2",
    "Anzahl Dateien": "file_count",
    "Größe Download": "download_size",
    "metalink": "metalink",
}


def process_regions_kml_file(
    kml_file_path: Optional[str] = None, kml_file_url: Optional[str] = None
) -> list[PortalBavariaRegionsKml]:
    """
    Parse a KML file and extract Placemark names and coordinates.

    :param kml_file_path: Path to a local KML file
    :param kml_file_url: URL to a KML file
    :return: List of placemark dicts
    """
    if not kml_file_path and not kml_file_url:
        raise ValueError("Either kml_file_path or kml_file_url must be provided.")
    if kml_file_path and kml_file_url:
        raise ValueError("Only one of kml_file_path or kml_file_url may be provided.")

    # --- Load file content ---
    if kml_file_path:
        if not os.path.exists(kml_file_path):
            raise FileNotFoundError(f"({kml_file_path}) does not exist.")
        with open(kml_file_path, "rb") as f:
            file_content = f.read()
    else:
        url: str = kml_file_url  # type: ignore[assignment]
        assert url is not None  # type checker knows it's str
        if not check_if_url_exists(url):
            raise FileNotFoundError(f"({url}) does not exist.")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        file_content = response.content

    # --- Parse KML ---
    root = ElementTree.fromstring(file_content)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    placemarks: list[PortalBavariaRegionsKml] = []

    for pm in root.findall(".//kml:Placemark", namespaces=ns):
        name_el = pm.find("kml:name", ns)
        desc_el = pm.find("kml:description", ns)

        if not (name_el is not None and name_el.text and name_el.text.strip()):
            continue
        if not (desc_el is not None and desc_el.text and desc_el.text.strip()):
            continue
        pm_name = name_el.text.strip() if name_el is not None else None

        desc_data = parse_description(desc_el.text.strip())
        pm_desc = normalize_kml_regions_description_values(desc_data)

        placemark = PortalBavariaRegionsKml(
            placemark_name=pm_name,
            placemark_file_count=pm_desc["file_count"],
            placemark_metalink=pm_desc["metalink"],
            placemark_area_km2=pm_desc["area_km2"],
            placemark_download_size=pm_desc["download_size"],
            placemark_download_size_mb=pm_desc["download_mb"],
        )

        placemarks.append(placemark)
    return placemarks


def parse_description(description: str) -> dict:
    if not description:
        return {}

    soup = BeautifulSoup(unescape_html(description), "html.parser")

    data: dict[str, str] = {}

    # readout table
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).rstrip(":")
            if key in KmlRegionsDescriptionTranslation:
                new_key = KmlRegionsDescriptionTranslation[key]
            else:
                new_key = key
            value = cells[1].get_text(strip=True)
            data[new_key] = value

    # extract metalink
    link = soup.find("a", href=True)
    if link:
        href: str
        if isinstance(link["href"], str):
            href = link["href"]
        else:
            href = " ".join(link["href"])  # if AttributeValueList
        data["metalink"] = href

    return data


def process_meta4_file(
    data_list: Optional[list[PortalBavariaRegionsKml]] = None,
    path_to_json: Optional[str] = None,
    timeout: int = 10,
    debug: bool = False,
) -> list[PortalBavariaMeta4]:
    """

    :param data_list:
    :param path_to_json:
    :param timeout:
    :param debug:
    :return: A list of PortalBavariaMeta4 objects
    """
    if data_list is None and path_to_json is None:
        raise ValueError("Either data_list or path_to_json must be provided.")
    if data_list is not None and path_to_json is not None:
        raise ValueError("Only one of data_list or path_to_json may be provided.")

    if path_to_json is not None:
        if not os.path.exists(path_to_json):
            raise FileNotFoundError(f"({path_to_json}) does not exist.")
        with open(path_to_json, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
        regions: list[PortalBavariaRegionsKml] = [PortalBavariaRegionsKml(**item) for item in raw_data]
    else:
        assert data_list is not None
        regions = data_list

    files: list[PortalBavariaMeta4] = []
    namespace = {"ml": "urn:ietf:params:xml:ns:metalink"}
    already_in_list: set[str] = set()

    for count, region in enumerate(regions, start=1):
        if debug:
            print(f"Processing region {count}/{len(regions)}...")
        if not region.placemark_metalink:
            continue
        try:
            response = requests.get(url=region.placemark_metalink, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch {region.placemark_metalink}") from exc

        root = ElementTree.fromstring(response.content)

        for file_elem in root.findall("ml:file", namespaces=namespace):
            file_name = file_elem.attrib.get("name")

            if not file_name or file_name in already_in_list:
                continue
            already_in_list.add(file_name)

            file_size_str = file_elem.findtext("ml:size", namespaces=namespace)
            file_size = int(file_size_str) if file_size_str else None
            file_hash_elem = file_elem.find("ml:hash", namespace)
            file_url = file_elem.findtext("ml:url", namespaces=namespace)

            if not file_size or not file_hash_elem or not file_url:
                continue
            files.append(
                PortalBavariaMeta4(
                    file_name=file_name,
                    file_size=file_size,
                    hash_type=file_hash_elem.attrib.get("type"),
                    hash_value=file_hash_elem.text if hasattr(file_hash_elem, "text") else None,
                    download_url=file_url,
                )
            )
    return files


def normalize_kml_regions_description_values(data: dict) -> dict:
    out = {}

    if "name" in data:
        out["name"] = data["name"].strip()

    if "area_km2" in data:
        out["area_km2"] = float(data["area_km2"].replace("km²", "").replace(",", ".").strip())

    if "file_count" in data:
        out["file_count"] = int(data["file_count"])

    if "download_size" in data:
        size_str = data["download_size"].replace(",", ".").strip()
        out["download_size"] = size_str

        if size_str.lower().endswith("gb"):
            value = float(size_str.lower().replace("gb", "").strip())
            out["download_mb"] = value * 1024
        elif size_str.lower().endswith("mb"):
            value = float(size_str.lower().replace("mb", "").strip())
            out["download_mb"] = value
        elif size_str.lower().endswith("kb"):
            value = float(size_str.lower().replace("kb", "").strip())
            out["download_kb"] = value / 1024
        else:
            raise TypeError(f"Unsupported download gb type: {data['download_gb']}")

    out["metalink"] = data.get("metalink")

    return out


def get_bavaria_geoportal_lidar_file_list(
    kml_file_path: Optional[str] = None,
    kml_file_url: Optional[str] = None,
    timeout: int = 10,
    debug: bool = False,
):
    """

    :param kml_file_path: Path to a local KML file
    :param kml_file_url: URL to a KML file
    :param timeout:
    :param debug:
    :return:
    """
    placemarks = process_regions_kml_file(kml_file_path, kml_file_url)
    write_data_to_file(
        data_class=PortalBavariaRegionsKml,
        data=placemarks,
        output_path="docs/output_bavaria_kml_regions.json",
        file_format="json",
    )
    tiles = process_meta4_file(
        data_list=placemarks,
        timeout=timeout,
        debug=debug,
    )
    write_data_to_file(
        data_class=PortalBavariaMeta4,
        data=tiles,
        output_path="docs/output_bavaria_laz_files.json",
        file_format="json",
    )
