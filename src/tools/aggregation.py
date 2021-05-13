import pandas as pd
import geopandas as gpd
from typing import Union


def aggregate_hex(edges_hex: Union[pd.DataFrame, gpd.GeoDataFrame]) -> pd.DataFrame:
    hex_feautres = edges_hex.drop(columns="id").groupby(by="h3_id").sum()
    return hex_feautres
