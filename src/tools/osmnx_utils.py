import osmnx as ox
import os
import unidecode
from shapely import speedups
from pathlib import Path
from typing import List, Optional

from src.tools.h3_utils import get_buffered_place_for_h3, get_resolution_buffered_suffix


# speedups.disable()  # fix for: ValueError: GEOSGeom_createLinearRing_r returned a NULL pointer
# print("Speedups enabled:", speedups.enabled)

def generate_data_for_place(place_name: str, data_dir: str, h3_resolutions: List[int], network_type: str, regions: Optional[List[str]]):
    place_dir = get_place_dir_name(place_name)
    out_dir = Path(data_dir).joinpath(place_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    download_and_save_data_for_place(place_name, out_dir, network_type, h3_resolutions, regions)


def download_and_save_data_for_place(place_name: str, out_dir: Path, network_type: str, h3_resolutions: List[int], regions: Optional[List[str]]):
    ox.config(timeout=10000)

    if regions is not None:
        by_osmid = isinstance(regions[0], tuple)
        regions = list(map(lambda x: x[0], regions)) if by_osmid else regions
        place = ox.geocode_to_gdf(regions, by_osmid=by_osmid).dissolve()
        place.display_name = f"{place_name.split(',')[0]}, " + place.display_name
    else:
        place = ox.geocode_to_gdf(place_name)

    place = place.explode()
    place["area"] = place.area
    place = place.sort_values(by="area", ascending=False).iloc[[0]]
    polygon = place.geometry.item()

    G = ox.graph_from_polygon(polygon, network_type=network_type, retain_all=True)

    ox.save_graphml(G, Path(out_dir) / f"graph_{network_type}.graphml", gephi=False)
    # ox.save_graphml(G, Path(out_dir) / f"graph_{network_type}_gephi.graphml", gephi=True)

    gpkg_path = Path(out_dir) / f"graph_{network_type}.gpkg"
    ox.save_graph_geopackage(G, gpkg_path)
    place.to_file(gpkg_path, layer="place", driver="GPKG")
    # place.to_file(out_dir / "place.geojson", driver="GeoJSON")

    for h3_res in h3_resolutions:
        place_buffered = get_buffered_place_for_h3(place, h3_res)  # type: ignore
        # place_buffered.to_file(out_dir / f"place_{get_resolution_buffered_suffix(h3_res, True)}.geojson", driver="GeoJSON")
        place_buffered.to_file(gpkg_path, layer=f"place_{get_resolution_buffered_suffix(h3_res, True)}", driver="GPKG")


def get_place_dir_name(place_name: str) -> str:
    return unidecode.unidecode(place_name).replace(",", "_").replace(' ', "-")
