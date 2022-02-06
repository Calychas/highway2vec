from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DatasetGenerationConfig:
    cities_filename: str
    continents: List[str]
    countries: List[str]
    resolution: int
    buffered: bool
    network_type: str
    intersection_based: bool
    scale_length: bool
    normalize_type: str
    featureset_transformation_filename: str
    featureset_selection_filename: str
    featureset_transformation: Optional[dict]
    featureset_selection: Optional[dict]


@dataclass
class ExperimentConfig:
    dataset_filename: str
    model_name: str
    mode: str
    test_cities: List[str]
    test_size: float
    random_seed: Optional[int]
    batch_size: int
    num_workers: int
    shuffle: bool
    hidden_dim: int
    enc_out_dim: Optional[int]
    latent_dim: int
    epochs: int
    kl_coeff: Optional[float]
    lr: float
