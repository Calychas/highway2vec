import umap
import pandas as pd
from typing import Tuple

def reduce_umap(df: pd.DataFrame, n_neighbors: int, n_components: int, metric: str, mapper=None) -> Tuple[pd.DataFrame, umap.UMAP]:
    if not mapper:
        mapper = umap.UMAP(n_neighbors, n_components, metric).fit(df.values)
    embedding = mapper.transform(df.values)

    embedding_df = pd.DataFrame(embedding, columns=[f"x_{i}" for i in range(embedding.shape[1])])  # type: ignore
    embedding_df.index = df.index

    return embedding_df, mapper