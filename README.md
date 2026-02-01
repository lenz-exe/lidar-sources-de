# lidar-sources-de

Unified LiDAR data source definitions for all German federal states (Python modules) for large-scale downloading and processing.  
Currently, only **Bavaria** is included, but more states will be added in the future.

---

## List of OpenData GeoPortal

| State                                                                               | License                                                           | Module           | coordinate system  | area size          |
|-------------------------------------------------------------------------------------|-------------------------------------------------------------------|------------------|--------------------|--------------------|
| [Bavaria](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=laserdaten) | [CC BY 4.0 ](https://creativecommons.org/licenses/by/4.0/deed.de) | PortalBavaria.py | UTM32 (EPSG:25832) | Tiling 1 km x 1 km |

> More German federal states will be added as they become available.

---


## Development Setup

Requires Python >= 3.13. Install dependencies via [Poetry](https://python-poetry.org/):
```bash
poetry install
```

---

# Example Usage
```python
from lidar_sources_de.portal_bavaria import get_bavaria_geoportal_lidar_file_list

# Provide a local .kml file or a URL from the GeoPortal Bavaria website
result = get_bavaria_geoportal_lidar_file_list(
    kml_file_path="docs/bavaria_gemeinde.kml"
)

print(result)
```
Notes:
- The function generates a list of all available `.laz` files from the GeoPortal Bavaria for a given `.kml` file.
- To obtain the `.kml` file or URL, visit the GeoPortal Bavaria and inspect the network requests in your browser.
