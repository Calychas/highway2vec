from os.path import join
import click
from src.tools.osmnx_utils import generate_data_for_place, get_place_dir_name
from src.tools.h3_utils import generate_hexagons_for_place, get_hexagons_for_edges, get_hexagons_filename
from src.tools.feature_extraction import generate_features_for_edges, FEATURES_TO_EXPLODE
import geopandas as gpd

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
    shp_dir = join(place_dir, f"shp_{network_type}")
    edges_path = join(shp_dir, "edges.shp")
    hexagons_path = join(place_dir, get_hexagons_filename(resolution, buffered))
    
    hexagons: gpd.GeoDataFrame = gpd.read_file(hexagons_path, driver="GeoJSON")  # type: ignore
    edges: gpd.GeoDataFrame = gpd.read_file(edges_path)  # type: ignore

    edges["h3_id"] = get_hexagons_for_edges(edges, hexagons)
    edges = edges.explode("h3_id").reset_index()  # type: ignore
    edges.to_file(join(shp_dir, f"edges_hex_{resolution}{'_buffered' if buffered else ''}.shp"))


@main.command()
@click.argument('place_dir', type=click.Path(file_okay=False))
@click.argument('network_type', default="drive")
@click.argument('resolution', default=9)
@click.argument('buffered', default=True)
def features(place_dir: str, network_type: str, resolution: int, buffered: bool):
    shp_dir = join(place_dir, f"shp_{network_type}")
    edges_path = join(shp_dir, f"edges_hex_{resolution}{'_buffered' if buffered else ''}.shp")
    edges: gpd.GeoDataFrame = gpd.read_file(edges_path)  # type: ignore

    edges_with_features = generate_features_for_edges(edges, FEATURES_TO_EXPLODE)
    edges_with_features = edges_with_features.explode("h3_id")

    edges_with_features.to_file(join(place_dir, f"edges_{network_type}_{resolution}{'_buffered' if buffered else ''}.geojson"), driver="GeoJSON")


if __name__ == "__main__":
    main()