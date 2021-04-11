from tools.osmnx_utils import generate_data_for_place
from tools.h3_utils import generate_hexagons_for_place
from settings import *
from os.path import join
import pandas as pd
import geopandas as gpd

def main():
    place_name = "Wrocław,Poland"
    # generate_data_for_place(place_name, GENERATED_DATA_DIR, network_type="drive")
    place_dir = join(GENERATED_DATA_DIR, place_name)
    place: gpd.GeoDataFrame = gpd.read_file(join(place_dir, "place.geojson"), driver="GeoJSON")  # type: ignore
    generate_hexagons_for_place(place, 9, save_data_dir=place_dir, buffer=True)


if __name__ == "__main__":
    main()

