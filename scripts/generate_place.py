import click
from src.tools.osmnx_utils import generate_data_for_place, get_place_dir_name
from src.tools.h3_utils import generate_hexagons_for_place, assign_hexagons_to_edges, get_resolution_buffered_suffix
from src.tools.feature_extraction import generate_features_for_edges, FEATURES_TO_EXPLODE
import geopandas as gpd
from pathlib import Path


@click.group()
def main():
    pass


@main.command()
@click.argument('place_name')
@click.argument('out_dir', type=click.Path(file_okay=False))
@click.argument('network_type', default="drive")
def download(place_name: str, out_dir: str, network_type: str):
    generate_data_for_place(place_name, out_dir, network_type)


@main.command()
@click.argument('place_path', type=click.Path(dir_okay=False))
@click.argument('out_dir', type=click.Path(file_okay=False))
@click.argument('resolution', default=9)
@click.argument('buffer', default=True)
def h3(place_path: str, out_dir: str, resolution: int, buffer: bool):
    click.echo(place_path)
    place: gpd.GeoDataFrame = gpd.read_file(place_path, driver="GeoJSON")  # type: ignore
    generate_hexagons_for_place(place, resolution, out_dir, buffer)


@main.command('assignh3')
@click.argument('place_dir', type=click.Path(file_okay=False))
@click.argument('network_type', default="drive")
@click.argument('resolution', default=9)
@click.argument('buffered', default=True)
def assign_h3(place_dir: str, network_type: str, resolution: int, buffered: bool):
    shp_dir = Path(place_dir).joinpath(f"shp_{network_type}")
    edges_path = Path(shp_dir).joinpath("edges.shp")
    hexagons_path = Path(place_dir).joinpath(f"hex_{get_resolution_buffered_suffix(resolution, buffered)}.geojson")
    
    hexagons: gpd.GeoDataFrame = gpd.read_file(hexagons_path, driver="GeoJSON")  # type: ignore
    edges: gpd.GeoDataFrame = gpd.read_file(edges_path)  # type: ignore

    edges = assign_hexagons_to_edges(edges, hexagons)
    edges.to_file(Path(shp_dir).joinpath(f"edges_hex_{get_resolution_buffered_suffix(resolution, buffered)}.shp"))


@main.command()
@click.argument('place_dir', type=click.Path(file_okay=False))
@click.argument('network_type', default="drive")
@click.argument('resolution', default=9)
@click.argument('buffered', default=True)
def features(place_dir: str, network_type: str, resolution: int, buffered: bool):
    shp_dir = Path(place_dir).joinpath(f"shp_{network_type}")
    edges_path = Path(shp_dir).joinpath(f"edges_hex_{get_resolution_buffered_suffix(resolution, buffered)}.shp")
    edges: gpd.GeoDataFrame = gpd.read_file(edges_path)  # type: ignore

    edges_with_features = generate_features_for_edges(edges, FEATURES_TO_EXPLODE)
    edges_with_features = edges_with_features.explode("h3_id")

    edges_with_features.to_file(Path(place_dir).joinpath(f"edges_{network_type}_{get_resolution_buffered_suffix(resolution, buffered)}.geojson"), driver="GeoJSON")


if __name__ == "__main__":
    main()
