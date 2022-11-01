import pandas as pd
import geopandas as gpd
from typing import Tuple, Union


def remap_cluster(df: Union[pd.DataFrame, gpd.GeoDataFrame], c: int) -> Tuple[pd.Series, int]:
    n_old = c - 1
    n_new = c
    col_old = f"cluster_{n_old}"
    col_new = f"cluster_{n_new}"
    count_old = f"count_{n_old}"
    count_new = f"count_{n_new}"

    c_old = df[[col_old]].value_counts().reset_index().rename(columns={0: count_old})
    c_new = df[[col_new]].value_counts().reset_index().rename(columns={0: count_new})
    c_merge = c_new.merge(c_old, left_on=count_new, right_on=count_old, how="outer")  # will break on two clusters having the same count, fix would be probably to look into dendrogram
    
    old_cluster_id = -1
    new_clusters_id = [-1, -1]
    try:
        old_cluster_id = c_merge[c_merge[col_new].isna()][col_old].item()
        new_clusters_id = c_merge[c_merge[count_old].isna()][col_new].values

        c_mapping = {int(row[col_new]): int(row[col_old]) for _, row in c_merge.dropna().iterrows()}

        first_new_cluster_count = c_new.set_index(col_new).loc[new_clusters_id[0]].item()
        second_new_cluster_count = c_new.set_index(col_new).loc[new_clusters_id[1]].item()

        if first_new_cluster_count >= second_new_cluster_count:
            c_mapping[new_clusters_id[0]] = old_cluster_id
            c_mapping[new_clusters_id[1]] = n_old
        else:
            c_mapping[new_clusters_id[0]] = n_old
            c_mapping[new_clusters_id[1]] = old_cluster_id

        return df[col_new].apply(lambda x: c_mapping[x]).astype(int).astype("category"), old_cluster_id
    except Exception as e:
        print(e, c, old_cluster_id, new_clusters_id)
        return df[col_new], -1
