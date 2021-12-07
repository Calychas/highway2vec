from dataclasses import dataclass, field
from typing import List, Optional


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
class ExperimentConfig:
    dataset_filename: str
    model_name: str
    test_cities: List[str]
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
