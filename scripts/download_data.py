import sys
import geopandas as gpd
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm, trange

PROJECT_DIR = Path().parent.parent.resolve()
sys.path.append(str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR.joinpath("src").resolve()))

from settings import *
import scripts.generate_place as gp
from src.tools.osmnx_utils import get_place_dir_name
import time
import warnings
warnings.filterwarnings("ignore")

network_type = "drive"
cities = pd.read_csv(RAW_DATA_DIR.joinpath("cities.csv"))
cities = cities[cities["city"] != "Poland"]  # TODO: remove

pbar_city = tqdm(cities.itertuples(), total=cities.shape[0])
for row in pbar_city:
    place_name = f"{row.city},{row.country}"
    place_dir_name = get_place_dir_name(place_name)
    pbar_city.set_description(place_name)

    try:
        pbar_commands = tqdm(total=4, leave=False, desc="Download")
        gp.download.callback(place_name, GENERATED_DATA_DIR, network_type)
        pbar_commands.update()

        pbar_commands.set_description("Generate H3")
        gp.h3.callback(GENERATED_DATA_DIR.joinpath(place_dir_name, "place.geojson"), GENERATED_DATA_DIR.joinpath(place_dir_name), 8, True)
        gp.h3.callback(GENERATED_DATA_DIR.joinpath(place_dir_name, "place.geojson"), GENERATED_DATA_DIR.joinpath(place_dir_name), 9, True)
        pbar_commands.update()

        pbar_commands.set_description("Assign H3")
        gp.assign_h3.callback(GENERATED_DATA_DIR.joinpath(place_dir_name), network_type, 8, True)
        gp.assign_h3.callback(GENERATED_DATA_DIR.joinpath(place_dir_name), network_type, 9, True)
        pbar_commands.update()

        pbar_commands.set_description("Generate features")
        gp.features.callback(GENERATED_DATA_DIR.joinpath(place_dir_name), network_type, 8, True)
        gp.features.callback(GENERATED_DATA_DIR.joinpath(place_dir_name), network_type, 9, True)
        pbar_commands.update()
    except Exception as e:
        print("\n\nFailed:", place_name, "\n", e)
