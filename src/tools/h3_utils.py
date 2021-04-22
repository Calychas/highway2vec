import pandas as pd
import geopandas as gpd
import h3
from shapely.geometry import Polygon, LineString
from typing import List, Optional
from tqdm.auto import tqdm
from pathlib import Path

tqdm.pandas()


def generate_hexagons_for_place(place: gpd.GeoDataFrame, resolution: int, save_data_dir: Optional[str], buffer=False) -> gpd.GeoDataFrame:
    if buffer:
        place = get_buffered_place_for_h3(place, resolution)

    polygon = place.geometry.item()
    polygon_geojson = gpd.GeoSeries([polygon]).__geo_interface__
    geometry_geojson = polygon_geojson["features"][0]["geometry"]
    h3_hexes = list(h3.polyfill_geojson(geometry_geojson, resolution))  # type: ignore

    h3_df = pd.DataFrame(None)
    h3_df["h3_id"] = h3_hexes
    h3_df["coordinates"] = h3_df["h3_id"].apply(lambda x: str(h3.h3_to_geo(x)))  # type: ignore
    h3_df["geometry"] = h3_df["h3_id"].apply(lambda x: Polygon(tuple(map(lambda x: (x[1], x[0]), h3.h3_to_geo_boundary(x)))))  # type: ignore
    h3_df["parent"] = h3_df["h3_id"].apply(lambda x: h3.h3_to_parent(x))  # type: ignore
    h3_df["children"] = h3_df["h3_id"].apply(lambda x: str(h3.h3_to_children(x)))  # type: ignore
    h3_df["resolution"] = h3_df["h3_id"].apply(lambda x: h3.h3_get_resolution(x))  # type: ignore
    
    h3_df.set_index("h3_id", inplace=True)

    h3_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(h3_df).set_crs(epsg=4326)  # type: ignore
    if save_data_dir:
        h3_gdf.to_file(Path(save_data_dir).joinpath(f"hex_{get_resolution_buffered_suffix(resolution, buffer)}.geojson"), driver="GeoJSON")

    return h3_gdf


def get_resolution_buffered_suffix(resolution: int, buffered: bool):
    return f"{resolution}{'_buffered' if buffered else ''}"


def get_buffered_place_for_h3(place: gpd.GeoDataFrame, resolution: int) -> gpd.GeoDataFrame:
    edge_length = h3.edge_length(resolution=resolution, unit="m")  # type: ignore
    return place.to_crs(epsg=3395).buffer(edge_length).to_crs(epsg=4326)


def assign_hexagons_to_edges(edges: gpd.GeoDataFrame, hexagons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(gpd.sjoin(edges, hexagons[["h3_id", "geometry"]], op="intersects", how="inner") \
        .drop(columns="index_right") \
        .reset_index() \
        .sort_values(by="index", ignore_index=True) \
        .rename(columns={"index": "id"}))
