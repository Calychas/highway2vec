from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_DIR.joinpath("data")
RAW_DATA_DIR = DATA_DIR.joinpath("raw")
PROCESSED_DATA_DIR = DATA_DIR.joinpath("processed")
GENERATED_DATA_DIR = DATA_DIR.joinpath("generated")