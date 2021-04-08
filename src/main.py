from tools.osmnx_utils import generate_data_for_place
from tools.h3_utils import generate_hexagons_for_place
from settings import *


def main():
    place_name = "Wrocław,Poland"
    generate_data_for_place(place_name, GENERATED_DATA_DIR)
    generate_hexagons_for_place(place_name, GENERATED_DATA_DIR, resolution=8)

if __name__ == "__main__":
    main()

