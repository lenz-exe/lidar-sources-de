import html
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from lidar_sources_de.bavaria.models import KmlItemDescription, PortalBavariaRegionsKml

KmlRegionsDescriptionTranslation = {
    "Gebiet": "name",
    "Fläche": "area_km2",
    "Anzahl Dateien": "file_count",
    "Größe Download": "download_size",
    "metalink": "metalink",
}


def parse_regions_kml(kml_content: str) -> list[PortalBavariaRegionsKml]:
    """
    Parse a kml file and extract placemark names and meta4 urls.

    :param kml_content: A string of a kml file content
    :return: A list of PortalBavariaRegionsKml objects
    """
    root = ElementTree.fromstring(kml_content)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks: list[PortalBavariaRegionsKml] = []
    for pm in root.findall(".//kml:Placemark", namespaces=ns):
        name_el = pm.find("kml:name", ns)
        desc_el = pm.find("kml:description", ns)

        if not (name_el is not None and name_el.text and name_el.text.strip()):
            continue
        if not (desc_el is not None and desc_el.text and desc_el.text.strip()):
            continue
        pm_name = name_el.text.strip()
        desc_data = parse_description(desc_el.text.strip())
        pm_desc = normalize_kml_regions_description_values(desc_data)

        placemark = PortalBavariaRegionsKml(
            placemark_name=pm_name,
            placemark_file_count=pm_desc.file_count,
            placemark_metalink=pm_desc.metalink,
            placemark_area_km2=pm_desc.area_km2,
            placemark_download_size=pm_desc.download_size,
            placemark_download_size_mb=pm_desc.download_size_mb,
        )

        placemarks.append(placemark)
    return placemarks


def parse_description(description: str) -> dict:
    """
    Parse the kml item description from a html table to a dictionary and
    translate the keys into english.

    :param description: A string from the klm item <description>...</description>
    :return: a readable dictionary
    """
    soup = BeautifulSoup(html.unescape(description), "html.parser")
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


def normalize_kml_regions_description_values(data: dict) -> KmlItemDescription:
    """
    Standardize values of the kml item description.

    :param data: description data from a kml item in dict format
    :return: a dataclass object of KmlItemDescription
    """
    try:
        name = data["name"].strip()

        area_km2 = float(data["area_km2"].replace("km²", "").replace(",", ".").strip())

        file_count = int(data["file_count"])

        download_size = data["download_size"].replace(",", ".").strip()
        download_size_mb = parse_size_to_mb(download_size)

        metalink = str(data.get("metalink"))

    except KeyError as exc:
        raise ValueError(f"Missing key in kml item description: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid value in kml item description: {data}") from exc

    return KmlItemDescription(
        name=name,
        area_km2=area_km2,
        file_count=file_count,
        download_size=download_size,
        download_size_mb=download_size_mb,
        metalink=metalink,
    )


def parse_size_to_mb(size: str) -> float:
    """
    Converting a string with a size into a float in MB.

    :param size: a string like: '52.2 GB'
    :return: A float representing the size in MB
    """
    size = size.replace(",", ".").strip().lower()

    units = {
        "gb": 1024,
        "mb": 1,
        "kb": 1 / 1024,
    }

    for unit, factor in units.items():
        if size.endswith(unit):
            value = float(size.removesuffix(unit).strip())
            return value * factor

    raise ValueError(f"Unsupported download size unit: {size}")
