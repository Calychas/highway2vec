import umap
import pandas as pd

def reduce_umap(df: pd.DataFrame, n_neighbors: int, n_components: int, metric: str):
    mapper = umap.UMAP(n_neighbors, n_components, metric).fit(df.values)
    embedding = mapper.transform(df.values)

    embedding_df = pd.DataFrame(embedding, columns=["x", "y"])

    return embedding_df, mapper