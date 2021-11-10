import sys
import geopandas as gpd
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm, trange
import json5 as json
from collections import namedtuple

PROJECT_DIR = Path().parent.parent.resolve()
sys.path.append(str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR.joinpath("src").resolve()))

from settings import *
import scripts.generate_place as gp
from src.tools.osmnx_utils import get_place_dir_name
import warnings
from src.tools.logger import logging, get_logger


with open(RAW_DATA_DIR / "featureset_transformation_default.jsonc", "r") as f:
    FEATURESET = json.load(f)

PipelineParameters = namedtuple("PipelineParameters", ["commands", "network_type", "hex_resolutions_static", "hex_resolutions_features", "buffer_features", "intersection_based"])

def main():
    warnings.filterwarnings("ignore")
    logger = get_logger(__name__, logging.INFO)

    cities = pd.read_csv(RAW_DATA_DIR / "cities.csv")
    cities = cities[cities["city"].isin(["Wrocław"])]  # TODO: remove

    pipeline_parameters_list = [
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [9], False, False),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [9], True, False),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [9], False, True),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [9], True, True),

        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [8], False, False),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [8], True, False),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [8], False, True),
        PipelineParameters([False, False, True], "drive", [6, 7, 8, 9, 10], [8], True, True),
    ]
   
    for pp in pipeline_parameters_list:
        logger.info(f"Pipeline parameters {pp}")
        pbar_city = tqdm(cities.itertuples(), total=cities.shape[0])
        for row in pbar_city:
            place_name = f"{row.city},{row.country},{row.continent}"
            
            place_dir_name = get_place_dir_name(place_name)
            place_dir = GENERATED_DATA_DIR / place_dir_name
            regions = eval(row.regions) if isinstance(row.regions, str) else [None]
            logger.info(f"Place name {place_name}")
            pbar_city.set_description(place_name)

            try:
                pbar_commands = tqdm(total=1 + len(pp.hex_resolutions_static) + len(pp.hex_resolutions_features), leave=False, desc="Downloading")
                if pp.commands[0]:
                    gp.download.callback(place_name, GENERATED_DATA_DIR, pp.network_type, pp.hex_resolutions_static, regions)
                pbar_commands.update()

                for h3_res_static in pp.hex_resolutions_static:
                    pbar_commands.set_description(f"Generating H3 for hex res: {h3_res_static}")
                    if pp.commands[1]:
                        gp.h3.callback(place_dir, h3_res_static, False, pp.network_type)
                        gp.h3.callback(place_dir, h3_res_static, True, pp.network_type)
                    pbar_commands.update()

                for hex_res_features in pp.hex_resolutions_features:
                    pbar_commands.set_description(f"Generating features for hex res: {hex_res_features}")
                    if pp.commands[2]:
                        gp.features.callback(place_dir, pp.network_type, hex_res_features, pp.buffer_features, pp.intersection_based, FEATURESET)
                    pbar_commands.update()
                    
            except Exception as e:
                logger.exception(f"{place_name}: {e}")

if __name__ == "__main__":
    main()
