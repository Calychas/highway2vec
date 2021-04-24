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
    for col_expl in features_to_explode:
        edges = edges.join(explode_and_pivot(edges, col_expl))
    
    columns_useless_to_drop = ["u", "v", "key", "from", "to", "length"]
    columns_new_to_drop = [f"{x}_new" for x in features_to_explode]
    columns_none_to_drop: List[str] = list(filter(lambda x: "None" in x, edges.columns)) # type: ignore

    columns_to_drop = list(itertools.chain(columns_useless_to_drop, columns_new_to_drop, columns_none_to_drop, features_to_explode))
    edges.drop(columns=columns_to_drop, inplace=True)
    return edges  # type: ignore


def explode_and_pivot(df: Union[pd.DataFrame, gpd.GeoDataFrame], column_name: str) -> pd.DataFrame:
    prefix = f"{column_name}_"
    new_column_name = f"{prefix}new"
    df[new_column_name] = df[column_name].apply(lambda x: convert_to_list(x, column_name))
    df_expl = df.explode(new_column_name)  # type: ignore
    df_expl[new_column_name] = df_expl[new_column_name].astype(str)  # type: ignore
    df_piv = df_expl.pivot(columns=new_column_name, values=new_column_name).add_prefix(prefix)
    df_piv[df_piv.notnull()] = 1
    df_piv = df_piv.fillna(0).astype(int)

    return df_piv


def melt_and_max(edges: gpd.GeoDataFrame, column_name: str, columns: List[str]) -> pd.Series:
    gdf = edges[columns + ["id"]].melt(id_vars = ["id"], value_vars=columns)
    gdf["variable"] = gdf["variable"].apply(lambda x: float(x.split("_")[1]))
    gdf["mul"] = gdf["variable"] * gdf["value"]
    gdf = gdf.groupby("id").max()[["mul"]].rename(columns={"mul": column_name})
    return gdf[column_name]
    

def convert_to_list(x: Any, column_name: str) -> list:
    # x = str(x)
    x = sanitize_and_normalize(x, column_name)

    try:
        x = eval(x)
    except NameError:
        pass # is a pure string and cannot be converted

    x_list = [x] if type(x) is not list else x
    x_list = [sanitize_and_normalize(x, column_name) for x in x_list]
    
    return x_list


def sanitize_and_normalize(x: Any, column_name: str) -> str:
    return normalize(sanitize(x, column_name), column_name)


def normalize(x: Any, column_name: str) -> str:
    if column_name == "width":
        if "[" not in x:
            x = round(float(x)) if x != 'None' else x
    
    return str(x)


def sanitize(x: Any, column_name: str) -> str:
    if column_name == "width":  # FIXME: doesn't convert units
        if type(x) is str and x != "None" and "[" not in x:
            n = len(x)
            for _ in range(n):
                try:
                    x = float(x)
                    break
                except ValueError:
                    x = x[0:-1]
            x = str(x)
    elif column_name == "maxspeed":
        x = None if ":" in str(x) else x

    return str(x)


# def convert_to_list(x: Any, column_name: str) -> list:
#     x = str(x).replace(':', "_")
#     try:
#         x = eval(x) if type(x) is str else x
#     except NameError:
#         pass
#     return [x] if type(x) is not list else x