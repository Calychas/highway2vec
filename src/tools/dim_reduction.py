import pandas as pd
from sklearn.manifold import TSNE


def reduce_tsne(
    df: pd.DataFrame, n_components: int, perplexity: int
) -> pd.DataFrame:
    embedding = TSNE(n_components, perplexity=perplexity).fit_transform(df.values)

    embedding_df = pd.DataFrame(
        embedding, # type: ignore
        columns=[f"z_{i}" for i in range(embedding.shape[1])],
        index=df.index
    )

    return embedding_df