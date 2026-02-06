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
## Example 1
```python
from lidar_sources_de.bavaria.client import PortalBavariaClient
from lidar_sources_de.bavaria.serializers import to_json

client = PortalBavariaClient(timeout=15, debug=True)
regions = client.load_regions_from_kml(
    url="https://services.atlas.bayern.de/proxy/?url=https%3A%2F%2Fgeodaten.bayern.de%2Fodd%2Fa%2Flaser%2Fmeta%2Fkml%2Fgemeinde.kml",
)
tiles = client.load_tiles(regions)

to_json(tiles, "docs/output_bavaria_tiles.json")
```
Notes:
- get the current possible `.laz` file urls out of kml url
- returns a json with all urls for the `.laz` files

## Example 2
```python
from lidar_sources_de.bavaria.client import PortalBavariaClient
from lidar_sources_de.bavaria.serializers import to_json

client = PortalBavariaClient(timeout=15, debug=True)
regions = client.load_regions_from_kml(path="docs/bavaria_gemeinde.kml")
tiles = client.load_tiles(regions)

print(f"Found tiles: {len(tiles)}")
```
Notes:
- get the current possible `.laz` file urls out of a local kml file path
- returns `tiles` in form of a list
