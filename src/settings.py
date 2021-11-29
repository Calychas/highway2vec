from pathlib import Path

RANDOM_SEED = 42

PROJECT_DIR = Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GENERATED_DATA_DIR = DATA_DIR / "generated"
FEATURES_DIR = DATA_DIR / "features"
RUNS_DATA_DIR = DATA_DIR / "runs"

ASSETS_DIR = PROJECT_DIR / "assets"

KEPLER_DIR = ASSETS_DIR / "keplergl"
KEPLER_CONFIG_DIR = KEPLER_DIR / "config"
KEPLER_VIS_DIR = KEPLER_DIR / "vis"

LOGS_DIR = PROJECT_DIR / "logs"

CHECKPOINTS_DIR = PROJECT_DIR / "checkpoints"
