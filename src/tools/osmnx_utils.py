import osmnx as ox
import os
from os.path import join
import unidecode
from shapely import speedups


speedups.disable()  # fix for: ValueError: GEOSGeom_createLinearRing_r returned a NULL pointer


def generate_data_for_place(place_name: str, data_dir: str, network_type="drive"):
    place_dir = get_place_dir_name(place_name)
    out_dir = join(data_dir, place_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    download_and_save_data_for_place(place_name, out_dir, network_type)


def download_and_save_data_for_place(place_name: str, out_dir: str, network_type: str):
    place = ox.geocode_to_gdf(place_name)
    place.to_file(join(out_dir, "place.geojson"), driver="GeoJSON")

    G = ox.graph_from_place(place_name, network_type=network_type)
    ox.save_graphml(G, join(out_dir, f"graph_{network_type}.graphml"))
    ox.save_graph_geopackage(G, join(out_dir, f"graph_{network_type}.gpkg"))

    shp_dir = join(out_dir, f"shp_{network_type}")
    ox.save_graph_shapefile(G, shp_dir)


def get_place_dir_name(place_name: str) -> str:
    return unidecode.unidecode(place_name).replace(",", "_")
