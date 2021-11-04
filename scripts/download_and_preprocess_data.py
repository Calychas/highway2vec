import sys
import geopandas as gpd
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm, trange
import logging
import json5 as json

PROJECT_DIR = Path().parent.parent.resolve()
sys.path.append(str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR.joinpath("src").resolve()))

from settings import *
import scripts.generate_place as gp
from src.tools.osmnx_utils import get_place_dir_name
import warnings
from src.settings import RAW_DATA_DIR

with open(RAW_DATA_DIR / "featureset_default.jsonc", "r") as f:
    FEATURESET = json.load(f)


def main():
    warnings.filterwarnings("ignore")
    logger = logging.getLogger(__name__)

    network_type = "drive"
    hex_resolutions_static = [6, 7, 8, 9, 10]
    hex_resolutions_features = [9]
    buffer_features = False
    intersection_based = False
    cities = pd.read_csv(RAW_DATA_DIR / "cities.csv")
    cities = cities[cities["city"] == "Wrocław"]  # TODO: remove

    pbar_city = tqdm(cities.itertuples(), total=cities.shape[0])
    for row in pbar_city:
        place_name = f"{row.city},{row.country}"
        place_dir_name = get_place_dir_name(place_name)
        place_dir = GENERATED_DATA_DIR / place_dir_name
        regions = eval(row.regions) if isinstance(row.regions, str) else [None]

        pbar_city.set_description(place_name)

        try:
            pbar_commands = tqdm(total=1 + len(hex_resolutions_static) + len(hex_resolutions_features), leave=False, desc="Downloading")

            gp.download.callback(place_name, GENERATED_DATA_DIR, network_type, hex_resolutions_static, regions)
            pbar_commands.update()

            for h3_res_static in hex_resolutions_static:
                pbar_commands.set_description(f"Generating H3 for hex res: {h3_res_static}")
                gp.h3.callback(place_dir, h3_res_static, False, network_type)
                gp.h3.callback(place_dir, h3_res_static, True, network_type)
                pbar_commands.update()

            for hex_res_features in hex_resolutions_features:
                pbar_commands.set_description(f"Generating features for hex res: {hex_res_features}")
                gp.features.callback(place_dir, network_type, hex_res_features, buffer_features, intersection_based, FEATURESET)
                pbar_commands.update()
                
        except Exception as e:
            logger.exception(f"{place_name}: {e}")

if __name__ == "__main__":
    main()
