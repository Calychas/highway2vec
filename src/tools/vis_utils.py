
import folium
import h3
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import plotly.express as px


FIGSIZE = (20, 18)
MAP_SOURCE = ctx.providers.CartoDB.Positron


def plot_clusters(df: pd.DataFrame):
    fig = px.scatter(df, x="x_0", y="x_1", color="cluster", width=800, height=700)
    return fig


def plot_hexagons_map(hexagons: gpd.GeoDataFrame, edges: gpd.GeoDataFrame, column: str) -> plt.Axes:
    _, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_aspect('equal')
    hexagons.to_crs(epsg=3857).plot(column=column, ax=ax, alpha=0.6, legend=True, cmap="tab20")
    edges.to_crs(epsg=3857).plot(ax=ax, color="black", alpha=0.6)
    ctx.add_basemap(ax, source=MAP_SOURCE)
    return ax

def plot_feature_map(gdf: gpd.GeoDataFrame, column: str) -> plt.Axes:
    _, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_aspect('equal')
    gdf.to_crs(epsg=3857).plot(ax=ax, column=column, alpha=1, legend=True)
    ctx.add_basemap(ax, source=MAP_SOURCE)
    return ax
