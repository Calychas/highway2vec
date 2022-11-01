import pandas as pd
import geopandas as gpd
import h3
from shapely.geometry import Polygon
from typing import Optional
from tqdm.auto import tqdm
from pathlib import Path

tqdm.pandas()


def generate_hexagons_for_place(
    place: gpd.GeoDataFrame,
    resolution: int,
    save_data_dir: Optional[str],
    network_type: str,
    buffer=False,
) -> gpd.GeoDataFrame:
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
    if save_data_dir and not h3_gdf.empty:
        h3_gdf.to_file(
            Path(save_data_dir) / f"graph_{network_type}.gpkg",
            layer=f"hex_{get_resolution_buffered_suffix(resolution, buffer)}",
            driver="GPKG",
        )

    return h3_gdf


def get_resolution_buffered_suffix(resolution: int, buffered: bool) -> str:
    return f"{resolution}{'_buffered' if buffered else ''}"


def get_edges_with_features_filename(
    network_type: str, resolution: int, buffered: bool, intersection_based: bool
) -> str:
    return f"edges_{network_type}_{get_resolution_buffered_suffix(resolution, buffered)}{'_intersection' if intersection_based else ''}.feather"


def get_buffered_place_for_h3(
    place: gpd.GeoDataFrame, resolution: int
) -> gpd.GeoDataFrame:  # FIXME: not sure if it works properly
    twice_edge_length = 2 * h3.edge_length(resolution=resolution, unit="m")  # type: ignore
    return place.copy().to_crs(epsg=3395).buffer(twice_edge_length).to_crs(epsg=4326)


def assign_hexagons_to_edges(
    edges: gpd.GeoDataFrame,
    hexagons: gpd.GeoDataFrame,
    nodes: Optional[gpd.GeoDataFrame],
) -> gpd.GeoDataFrame:
    hexagons = gpd.GeoDataFrame(hexagons[["h3_id", "geometry"]])

    if nodes is None:
        edges_with_hexagons = gpd.GeoDataFrame(
            gpd.sjoin(edges, hexagons, op="intersects", how="inner")
            .drop(columns="index_right")
            .reset_index()
            .sort_values(by="index", ignore_index=True)
            .rename(columns={"index": "id"})
        )
    else:
        nodes = nodes.sjoin(hexagons, op="intersects", how="inner").set_index("osmid")[
            ["h3_id"]
        ]
        edges_with_hexagons = gpd.GeoDataFrame(
            pd.concat(
                [
                    nodes.merge(edges, left_index=True, right_on="u"),
                    nodes.merge(edges, left_index=True, right_on="v"),
                ]
            )
            .drop_duplicates()
            .sort_index()
            .reset_index()
            .rename(columns={"index": "id"})
        )

    return edges_with_hexagons
