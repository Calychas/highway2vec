from typing import Union, Any, List
import pandas as pd
import geopandas as gpd
import itertools


FEATURES_TO_EXPLODE = [
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


def generate_features_for_edges(edges: Union[pd.DataFrame, gpd.GeoDataFrame], features_to_explode: List[str]) -> gpd.GeoDataFrame:
    edges.rename(columns={"index": "id"}, inplace=True)
    for col_expl in features_to_explode:
        edges = edges.join(explode_and_pivot(edges, col_expl))
    
    columns_useless_to_drop = ["u", "v", "key", "from", "to", "length"]
    columns_new_to_drop = [f"{x}_new" for x in features_to_explode]
    columns_none_to_drop: List[str] = list(filter(lambda x: "None" in x, edges.columns)) # type: ignore

    columns_to_drop = list(itertools.chain(columns_useless_to_drop, columns_new_to_drop, columns_none_to_drop, features_to_explode))
    edges.drop(columns=columns_to_drop, inplace=True)
    return edges  # type: ignore


def explode_and_pivot(df: Union[pd.DataFrame, gpd.GeoDataFrame], column_name: str) -> pd.DataFrame:
    new_column_name = f"{column_name}_new"
    df[new_column_name] = df[column_name].apply(convert_to_list)
    df_expl = df.explode(new_column_name)  # type: ignore
    prefix = f"{column_name}_"
    df_expl[new_column_name] = df_expl[new_column_name].astype(str)  # type: ignore
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
