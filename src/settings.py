from pathlib import Path
import logging
from datetime import datetime

RANDOM_SEED = 42

PROJECT_DIR = Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GENERATED_DATA_DIR = DATA_DIR / "generated"

ASSETS_DIR = PROJECT_DIR / "assets"

KEPLER_DIR = ASSETS_DIR / "keplergl"
KEPLER_CONFIG_DIR = KEPLER_DIR / "config"
KEPLER_VIS_DIR = KEPLER_DIR / "vis"

LOGS_DIR = PROJECT_DIR / "logs"


logging.basicConfig(
    handlers=[
        logging.FileHandler(LOGS_DIR / datetime.now().strftime('logfile_%Y-%m-%d_%H-%M-%S.log')),
        logging.StreamHandler()
    ],
    format='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
    level=logging.WARNING
)
