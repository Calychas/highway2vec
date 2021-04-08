import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Any
import osmnx as ox
import os
from os.path import join


COLUMNS_TO_EXPLODE = [
    "oneway",
    "lanes",
    "highway",
    "maxspeed",
    "bridge",
    "access",
    "junction",
    "width",
    "tunnel"
]


def generate_data_for_place(place_name: str, data_dir: str, network_type="drive", columns_to_explode=COLUMNS_TO_EXPLODE):
    out_dir = join(data_dir, place_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)


    place = ox.geocode_to_gdf(place_name)
    place.to_file(join(out_dir, "place.geojson"), driver="GeoJSON")

    G = ox.graph_from_place(place_name, network_type=network_type)
    ox.save_graphml(G, join(out_dir, f"graph_{network_type}.graphml"))
    ox.save_graph_geopackage(G, join(out_dir, f"graph_{network_type}.gpkg"))

    shp_dir = join(out_dir, f"shp_{network_type}")
    ox.save_graph_shapefile(G, shp_dir)
    edges = gpd.read_file(join(shp_dir, "edges.shp"))

    edges.reset_index(inplace=True)

    for col_expl in columns_to_explode:
        edges = edges.join(explode_and_pivot(edges, col_expl))
    
    columns_to_drop = [f"{x}_new" for x in columns_to_explode]
    edges.drop(columns=columns_to_drop).to_file(join(out_dir, f"edges_{network_type}.geojson"), driver="GeoJSON")


def explode_and_pivot(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    new_column_name = f"{column_name}_new"
    df[new_column_name] = df[column_name].apply(convert_to_list)
    df_expl = df.explode(new_column_name)  # type: ignore
    prefix = f"{column_name}_"
    df_expl[new_column_name] = df_expl[new_column_name].astype(str)
    df_piv = df_expl.pivot(columns=new_column_name, values=new_column_name).add_prefix(prefix)
    df_piv[df_piv.notnull()] = 1
    df_piv = df_piv.fillna(0).astype(int)

    return df_piv


def convert_to_list(x: Any) -> list:
    try:
        x = eval(x) if type(x) is str else x
    except NameError:
        pass
    return [x] if type(x) is not list else x
