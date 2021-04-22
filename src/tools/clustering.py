
import pandas as pd
import hdbscan


def cluster_hdbscan(df: pd.DataFrame, min_cluster_size: int, metric: str) -> pd.Series:
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric=metric)
    cluster_labels = clusterer.fit_predict(df)

    return pd.Series(cluster_labels).astype("category")