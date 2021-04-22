
import folium
import h3
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import plotly.express as px


FIGSIZE = (25, 20)
MAP_SOURCE = ctx.providers.CartoDB.Positron


def plot_clusters(df: pd.DataFrame):
    fig = px.scatter(df, x="x", y="y", color="cluster", width=800, height=700)
    return fig


def plot_feature_map(gdf: gpd.GeoDataFrame, column: str):
    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE)
    ax.set_aspect('equal')
    gdf.to_crs(epsg=3857).plot(ax=ax, column=column, alpha=1, legend=True)
    ctx.add_basemap(ax, source=MAP_SOURCE)
    return ax


def visualize_hexagons(hexagons, color="red", folium_map=None, width=8):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons. 
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)  # type: ignore
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v:v[0],polyline))
        lng.extend(map(lambda v:v[1],polyline))
        polylines.append(polyline)
    
    if folium_map is None:
        f = folium.Figure(width=1000, height=500)
        m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)], zoom_start=13, tiles='cartodbpositron').add_to(f)
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine=folium.PolyLine(locations=polyline,weight=width,color=color)
        m.add_child(my_PolyLine)
    return m
    

def visualize_polygon(polyline, color):
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)], zoom_start=13, tiles='cartodbpositron')
    my_PolyLine=folium.PolyLine(locations=polyline,weight=8,color=color)
    m.add_child(my_PolyLine)
    return m