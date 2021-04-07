from os.path import normpath, dirname, join

PROJECT_DIR = normpath(dirname(__file__))

DATA_DIR = join(PROJECT_DIR, "data")
RAW_DATA_DIR = join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = join(DATA_DIR, "processed")
GENERATED_DATA_DIR = join(DATA_DIR, "generated")