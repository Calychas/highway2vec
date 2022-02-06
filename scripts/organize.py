from importlib.resources import path
from pathlib import Path
import shutil
import unidecode


path_to_data = Path("D:\\Projekty\\Programowanie\\Studia\\Semestr10\\gis\\osm-road-infrastructure\\data\\runs\\rose-sun-44\\vis\\hexagons")
files = path_to_data.glob("*")

clusters = list(range(2, 12 + 1))

for c in clusters:
    (path_to_data / f"c{c}").mkdir(exist_ok=True)

for file in files:
    for c in clusters:
        if f"_{c}." in file.name:
            shutil.copy(file, path_to_data / f"c{c}" / unidecode.unidecode(file.name.rsplit("_", 2)[0] + "_hexagons" + ".png"))