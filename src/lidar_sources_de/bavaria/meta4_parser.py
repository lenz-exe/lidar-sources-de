from xml.etree import ElementTree

import requests

from lidar_sources_de.bavaria.models import PortalBavariaMeta4, PortalBavariaRegionsKml


def parse_meta4_file(
    regions: list[PortalBavariaRegionsKml],
    timeout: int = 10,
    debug: bool = False,
) -> list[PortalBavariaMeta4]:
    """
    Parsing Meta4 file into a list of dataclass PortalBavariaMeta4.

    :param regions: A list of PortalBavariaRegionsKml objects
    :param timeout: An int (seconds) how long to wait for a response
    :param debug: a boolean to activate the debug mode for more printing
    :return: A list of PortalBavariaMeta4 objects
    """
    files: list[PortalBavariaMeta4] = []
    namespace = {"ml": "urn:ietf:params:xml:ns:metalink"}
    seen: set[str] = set()

    for count, region in enumerate(regions, start=1):
        if debug:
            print(f"Parsing region {count} of {len(regions)}")
        if not region.placemark_metalink:
            if debug:
                print(
                    f"Skipping region {count} of {len(regions)} ({region.placemark_name}), "
                    "because no placemark metalink found"
                )
            continue
        resp = requests.get(region.placemark_metalink, timeout=timeout)
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)

        for f in root.findall("ml:file", namespaces=namespace):
            file_name = f.attrib.get("name")
            if not file_name or file_name in seen:
                continue
            seen.add(file_name)

            file_size_str = f.findtext("ml:size", namespaces=namespace)
            file_size = int(file_size_str) if file_size_str else None
            file_url = f.findtext("ml:url", namespaces=namespace)
            file_hash_value = f.findtext("ml:hash", namespaces=namespace)
            file_hash_elm = f.find("ml:hash", namespaces=namespace)
            if hasattr(file_hash_elm, "attrib"):
                file_hash_type = file_hash_elm.attrib.get("type", "unknown")
            else:
                file_hash_type = "unknown"

            if not file_size or not file_url or not file_hash_value or not file_hash_type:
                print(f"skipping file {file_name} from region {region.placemark_name}")
                continue

            files.append(
                PortalBavariaMeta4(
                    file_name=file_name,
                    file_size=file_size,
                    hash_type=file_hash_type,
                    hash_value=file_hash_value,
                    download_url=file_url,
                )
            )
    return files
