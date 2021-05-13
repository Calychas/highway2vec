import pandas as pd
import hdbscan
from typing import Tuple


def cluster_hdbscan(
    df: pd.DataFrame,
    min_cluster_size: int,
    metric: str,
    clusterer: hdbscan.HDBSCAN = None,
) -> Tuple[pd.Series, hdbscan.HDBSCAN]:
    if not clusterer:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric=metric)
    cluster_labels = clusterer.fit_predict(df)

    return pd.Series(cluster_labels, index=df.index).astype("category"), clusterer