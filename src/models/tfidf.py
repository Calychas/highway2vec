from sklearn.feature_extraction.text import TfidfTransformer
import pandas as pd


def tfidf(df: pd.DataFrame) -> pd.DataFrame:
    v = TfidfTransformer()
    x = v.fit_transform(df)
    df_tfidf = pd.DataFrame(x.toarray(), index=df.index, columns=df.columns)

    return df_tfidf
