from os.path import join
import pandas as pd
import geopandas as gpd
import h3
from shapely.geometry import Polygon, LineString
from typing import List, Optional
from tqdm.auto import tqdm


tqdm.pandas()


def generate_hexagons_for_place(place: gpd.GeoDataFrame, resolution: int, save_data_dir: Optional[str], buffer=False) -> gpd.GeoDataFrame:
    if buffer:
        place = get_buffered_place_for_h3(place, resolution)

    polygon = place.geometry.item()
    polygon_geojson = gpd.GeoSeries([polygon]).__geo_interface__
    geometry_geojson = polygon_geojson["features"][0]["geometry"]
    h3_hexes = list(h3.polyfill_geojson(geometry_geojson, resolution))  # type: ignore

    h3_df = pd.DataFrame(None)
    h3_df["id"] = h3_hexes
    h3_df["coordinates"] = h3_df["id"].apply(lambda x: str(h3.h3_to_geo(x)))  # type: ignore
    h3_df["geometry"] = h3_df["id"].apply(lambda x: Polygon(tuple(map(lambda x: (x[1], x[0]), h3.h3_to_geo_boundary(x)))))  # type: ignore
    h3_df["parent"] = h3_df["id"].apply(lambda x: h3.h3_to_parent(x))  # type: ignore
    h3_df["children"] = h3_df["id"].apply(lambda x: str(h3.h3_to_children(x)))  # type: ignore
    h3_df["resolution"] = h3_df["id"].apply(lambda x: h3.h3_get_resolution(x))  # type: ignore

    h3_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(h3_df).set_crs(epsg=4326)  # type: ignore
    if save_data_dir:
        h3_gdf.to_file(join(save_data_dir, get_hexagons_filename(resolution, buffer)), driver="GeoJSON")

    return h3_gdf


def get_hexagons_filename(resolution: int, buffered: bool):
    return f"hex_{resolution}{'_buffered' if buffered else ''}.geojson"


def get_buffered_place_for_h3(place: gpd.GeoDataFrame, resolution: int) -> gpd.GeoDataFrame:
    edge_length = h3.edge_length(resolution=resolution, unit="m")  # type: ignore
    return place.to_crs(epsg=3395).buffer(int(edge_length)).to_crs(epsg=4326)


def get_hexagons_for_edges(edges: gpd.GeoDataFrame, hexagons: gpd.GeoDataFrame, verbose=True) -> pd.Series:
    if verbose:
        hexes_for_lines = edges["geometry"].progress_apply(lambda x: get_hexagons_for_edge(x, hexagons))
    else:
        hexes_for_lines = edges["geometry"].apply(lambda x: get_hexagons_for_edge(x, hexagons))

    return hexes_for_lines  # type: ignore


def get_hexagons_for_edge(edge: LineString, hexagons_gdf: gpd.GeoDataFrame) -> List[str]:
    return hexagons_gdf[hexagons_gdf.intersects(edge)]["id"].to_list()  # type: ignore

