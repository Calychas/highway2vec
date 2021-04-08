from os.path import join
import pandas as pd
import geopandas as gpd
import h3
import folium
from shapely.geometry import Polygon


def generate_hexagons_for_place(place_name: str, data_dir: str, resolution=8):
    place_dir = join(data_dir, place_name)
    place = gpd.read_file(join(place_dir, "place.geojson"), driver="GeoJSON")
    polygon = place.geometry.item()
    polygon_geojson = gpd.GeoSeries([polygon]).__geo_interface__
    geometry_geojson = polygon_geojson["features"][0]["geometry"]
    h3_hexes = list(h3.polyfill_geojson(geometry_geojson, resolution))

    h3_df = pd.DataFrame(None)
    h3_df["id"] = h3_hexes
    h3_df["coordinates"] = h3_df["id"].apply(lambda x: str(h3.h3_to_geo(x)))
    h3_df["geometry"] = h3_df["id"].apply(lambda x: Polygon(tuple(map(lambda x: (x[1], x[0]), h3.h3_to_geo_boundary(x)))))
    h3_df["parent"] = h3_df["id"].apply(lambda x: h3.h3_to_parent(x))
    h3_df["children"] = h3_df["id"].apply(lambda x: str(h3.h3_to_children(x)))
    h3_df["resolution"] = h3_df["id"].apply(lambda x: h3.h3_get_resolution(x))

    h3_gdf = gpd.GeoDataFrame(h3_df).set_crs(epsg=4326)
    h3_gdf.to_file(join(place_dir, f"hex_{resolution}.geojson"), driver="GeoJSON")


def visualize_hexagons(hexagons, color="red", folium_map=None, width=8):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons. 
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
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