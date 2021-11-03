
import folium
import h3
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import plotly.express as px
from typing import Union, Dict
from keplergl import KeplerGl
import json
from src.settings import *
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from geopandas import GeoDataFrame
from shapely import wkt


FIGSIZE = (20, 18)
KEPLER_HEIGHT = 900
MAP_SOURCE = ctx.providers.CartoDB.Positron


def ensure_geometry_type(
    df: GeoDataFrame, geometry_column: str = "geometry"
) -> GeoDataFrame:
    def ensure_geometry_type_correct(geometry):
        if type(geometry) == str:
            return wkt.loads(geometry)
        else:
            return geometry

    if geometry_column in df.columns:
        df[geometry_column] = df[geometry_column].apply(ensure_geometry_type_correct)
    return df


def save_config(kepler: KeplerGl, config_name: str) -> Path:
    path = KEPLER_CONFIG_DIR / f"{config_name}.json"
    with open(path, "wt") as f:
        json.dump(kepler.config, f)
    return path


def load_config(config_name: str) -> Union[Dict, None]:
    try:
        with open(KEPLER_CONFIG_DIR / f"{config_name}.json", "rt") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def visualize_kepler(data: Union[pd.DataFrame, gpd.GeoDataFrame], name="data", config_name: str=None) -> KeplerGl:
    ensure_geometry_type(data)
    if config_name is not None:
        config = load_config(config_name)
        if config is not None:
            return KeplerGl(data={name: data}, config=config, height=KEPLER_HEIGHT)
    return KeplerGl(data={name: data}, height=KEPLER_HEIGHT)


def save_kepler_map(kepler_map: KeplerGl, figure_subpath: Path, remove_html=False):
    result_path = KEPLER_VIS_DIR / figure_subpath
    result_path.parent.mkdir(parents=True, exist_ok=True)
    html_file = result_path.with_suffix(".html")
    
    for gdf in kepler_map.data.values():
        ensure_geometry_type(gdf)
    kepler_map.save_to_html(file_name=html_file)

    options = Options()
    height = kepler_map.height
    width = 1300
    options.add_argument("--headless")
    options.add_argument(f"--window-size={width},{height}")

    driver = webdriver.Chrome(options=options)
    driver.get(str(html_file.resolve()))
    time.sleep(3)
    driver.save_screenshot(str(result_path))
    if remove_html:
        html_file.unlink()


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
