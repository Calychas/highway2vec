import pickle as pkl
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import sys
from pathlib import Path

PROJECT_DIR = Path().parent.parent.resolve()
sys.path.append(str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR.joinpath("src").resolve()))

import geopandas as gpd
import json5 as json
import pandas as pd
from src.settings import *
from src.tools.feature_extraction import apply_feature_selection, normalize_df
from src.tools.h3_utils import (get_edges_with_features_filename,
                                get_resolution_buffered_suffix)
from src.tools.osmnx_utils import get_place_dir_name
from tqdm.auto import tqdm


@dataclass
class DatasetGenerationConfig:
    cities_filename: str = "cities.csv"
    countries: List[str] = field(default_factory=lambda: ["Poland"])
    resolution: int = 9
    buffered: bool = True
    network_type: str = "drive"
    intersection_based: bool = False
    scale_length: bool = True
    normalize_type: str = "global"
    featureset_transformation_filename: str = "featureset_transformation_default.jsonc"
    featureset_selection_filename: str = "featureset_selection_1.jsonc"
    featureset_transformation: Optional[dict] = None
    featureset_selection: Optional[dict] = None


@dataclass
class SpatialDataset:
    config: DatasetGenerationConfig
    cities: pd.DataFrame
    edges: gpd.GeoDataFrame
    hexagons: gpd.GeoDataFrame
    hex_agg: Optional[pd.DataFrame]
    hex_agg_normalized: Optional[pd.DataFrame]


def main(cfg: DatasetGenerationConfig):
    cities = pd.read_csv(RAW_DATA_DIR / cfg.cities_filename)
    cities = cities[(cities.country.isin(cfg.countries)) & (cities.kacper)]

    with open(RAW_DATA_DIR / cfg.featureset_transformation_filename, "r") as f:
        featureset = json.load(f)
    features_transformation = [f"{k}_{v}" for k, vs in featureset.items() for v in vs]

    cfg.featureset_transformation = featureset

    resolution = cfg.resolution
    buffered = cfg.buffered
    network_type = cfg.network_type
    intersection_based = cfg.intersection_based
    index_columns = ["continent", "country", "city", "h3_id"]

    pbar = tqdm(cities.itertuples(), total=cities.shape[0])
    hexagons = []
    edges = []
    for row in pbar:
        place_name = f"{row.city},{row.country}"
        place_dir_name = get_place_dir_name(place_name)
        place_dir_path = GENERATED_DATA_DIR / place_dir_name
        gpkg_path = place_dir_path / f"graph_{network_type}.gpkg"
        pbar.set_description(place_name)

        try:
            hexagons_city = gpd.read_file(gpkg_path, layer=f"hex_{get_resolution_buffered_suffix(resolution, buffered)}")
            hexagons_city["city"] = row.city
            hexagons_city["country"] = row.country
            hexagons_city["continent"] = row.continent
            hexagons.append(hexagons_city)

            edges_city = gpd.read_feather(place_dir_path / get_edges_with_features_filename(network_type, resolution, buffered, intersection_based))
            # edges_city[features_transformation] = edges_city[features_transformation].astype(sparse_dtype)
            edges_city[features_transformation] = edges_city[features_transformation].astype("int32")
            edges_city["city"] = row.city
            edges_city["country"] = row.country
            edges_city["continent"] = row.continent
            edges.append(edges_city)
        except Exception as e:
            print("\nFailed", place_name, e)
        

    hexagons = gpd.GeoDataFrame(pd.concat(hexagons, ignore_index=True).set_index(index_columns))
    edges = gpd.GeoDataFrame(pd.concat(edges)).set_index(index_columns).set_crs(epsg=4326)
    edges["length"] = edges.to_crs(epsg=3857).length

    del hexagons_city
    del edges_city


    scale_length = cfg.scale_length

    with open(RAW_DATA_DIR / cfg.featureset_selection_filename, "r") as f:
        featureset_selection_config = json.load(f)
    edges_feature_selection = apply_feature_selection(edges, featureset_selection_config, scale_length=scale_length)

    cfg.featureset_selection = featureset_selection_config
    
    hex_agg = edges_feature_selection.groupby(level=index_columns).sum()

    normalize_type = cfg.normalize_type
    hex_agg_normalized = normalize_df(hex_agg, type=normalize_type)

    dataset = SpatialDataset(cfg, cities, edges, hexagons, hex_agg, hex_agg_normalized)
    with open(FEATURES_DIR / f"dataset_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl.gz", "wb") as f:
        pkl.dump(dataset, f)


if __name__ == "__main__":
    main(DatasetGenerationConfig())
