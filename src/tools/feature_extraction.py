from typing import Union, Any, List, Dict
import pandas as pd
import geopandas as gpd
import itertools


FEATURESET = {
    "oneway": ["0", "1"],
    "lanes": ["1", "2", "3", "4", "5", "6", "7"],
    "highway": [
        "living_street",
        "motorway",
        "motorway_link",
        "primary",
        "primary_link",
        "residential",
        "secondary",
        "secondary_link",
        "tertiary",
        "tertiary_link",
        "trunk",
        "trunk_link",
        "unclassified",
    ],
    "maxspeed": [
        "5",
        "7",
        "10",
        "15",
        "20",
        "30",
        "40",
        "50",
        "60",
        "70",
        "80",
        "90",
        "100",
        "110",
        "120",
        "130",
        "140",
        "150",
        "160",
    ],
    "bridge": [
        "yes",
        # "no",
        "aqueduct",
        "boardwalk",
        "cantilever",
        "covered",
        "low_water_crossing",
        "movable",
        "trestle",
        "viaduct",
    ],
    "access": [
        "yes",
        "no",
        "private",
        "permissive",
        "permit",
        "destination",
        "delivery",
        "customers",
        "designated",
        "use_sidepath",
        "dismount",
        "agricultural",
        "forestry",
        "discouraged",
        "unknown",
    ],
    "junction": ["roundabout", "circular", "jughandle", "filter"],
    "width": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "1.5",
        "2.5",
        "3.5",
        "4.5",
        "5.5",
        "6.5",
        "7.5",
        "8.5",
        "9.5",
        "10.5",
        "11.5",
        "12.5",
        "13.5",
        "14.5",
        "15.5",
        "16.5",
        "17.5",
        "18.5",
        "19.5",
        "20.5",
        "21.5",
        "22.5",
        "23.5",
        "24.5",
        "25.5",
        "26.5",
        "27.5",
        "28.5",
        "29.5",
    ],
    "tunnel": [
        "building_passage",
        "yes",
        # "no",
        "avalanche_protector",
    ],
}


def generate_features_for_edges(
    edges: Union[pd.DataFrame, gpd.GeoDataFrame], featureset: Dict[str, List[str]]
) -> gpd.GeoDataFrame:
    for feature in featureset.keys():
        if feature in edges:
            edges = edges.join(explode_and_pivot(edges, feature))

    feature_column_names = list(
        itertools.chain(*[[f"{k}_{v}" for v in vs] for k, vs in featureset.items()])
    )
    columns_to_keep = ["id", "h3_id", "geometry"] + feature_column_names
    columns_to_drop = list(set(edges.columns) - set(columns_to_keep))
    columns_to_add = list(
        set(columns_to_keep) - (set(columns_to_keep).intersection(set(edges.columns)))
    )

    edges.drop(columns=columns_to_drop, inplace=True)

    for c in columns_to_add:
        edges[c] = 0

    edges = edges.reindex(columns_to_keep, axis=1)

    return gpd.GeoDataFrame(edges)  # type: ignore


def explode_and_pivot(
    df: Union[pd.DataFrame, gpd.GeoDataFrame], column_name: str
) -> pd.DataFrame:
    prefix = f"{column_name}_"
    new_column_name = f"{prefix}new"
    df[new_column_name] = df[column_name].apply(
        lambda x: convert_to_list(x, column_name)
    )
    df_expl = df.explode(new_column_name)  # type: ignore
    df_expl[new_column_name] = df_expl[new_column_name].astype(str)  # type: ignore
    df_piv = df_expl.pivot(columns=new_column_name, values=new_column_name).add_prefix(
        prefix
    )
    df_piv[df_piv.notnull()] = 1
    df_piv = df_piv.fillna(0).astype(int)

    return df_piv


def melt_and_max(
    edges: gpd.GeoDataFrame, column_name: str, columns: List[str]
) -> pd.Series:
    gdf = edges.groupby("id").first().drop(columns="h3_id").reset_index()
    gdf = gdf[["id"] + columns].melt(id_vars="id", value_vars=columns)
    gdf["variable"] = gdf["variable"].apply(lambda x: float(x.split("_")[1]))
    gdf["mul"] = gdf["variable"] * gdf["value"]
    gdf = gdf.groupby("id").max()[["mul"]].rename(columns={"mul": column_name})
    return gdf


def convert_to_list(x: Any, column_name: str) -> list:
    x = sanitize_and_normalize(x, column_name)

    try:
        x = eval(x)
    except NameError:
        pass  # is a pure string and cannot be evaled

    x_list = [x] if type(x) is not list else x
    x_list = [sanitize_and_normalize(x, column_name) for x in x_list]

    return x_list


def sanitize_and_normalize(x: Any, column_name: str) -> str:
    return normalize(sanitize(x, column_name), column_name)


def normalize(x: Any, column_name: str) -> str:
    if column_name == "width":
        if "[" not in x:
            if x != "None":
                x = min(
                    round(float(x) * 2) / 2, 30.0
                )  # FIXME: very bad max cap, doesnt depend on featureset
                 
    return str(x)


def sanitize(x: Any, column_name: str) -> str:
    if column_name == "width":  # FIXME: doesn"t convert units and will crash on inches
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
