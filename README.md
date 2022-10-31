## [Link to repository]()
## [Link to paper]()

<br>

## Goals
 <b>> Find representations (embeddings) of microregions with respect to their road network characteristics </b>

<b>> Define a typology of such regions</b>

<br>

## Data
### OSM
![OSM query](images/osm_query.jpg)

### Road Network
![](images/wroclaw_edges.jpg)

### Used Cities
![](images/cities_europe_all.jpg)


### Features

![](images/road_example.jpg)
| Tag | Description |
| --- | ----------- |
| oneway | whether the road is one-way |
| highway | rank of the road |
| surface | physical surface, structure, composition |
| maxspeed | maximum legal speed limit |
| lanes | number of traffic lanes |
| bridge | type of bridge that the way is on |
| junction | type of junction that the way forms itself |
| access | restrictions on the use |
| tunnel | type of an underground passage |
| width | actual width of a way |

<br>

## Microregions
Used [Uber's H3](https://h3geo.org/) (hexagonal hierarchical geospatial indexing system).
![Hex Resolution comparison](images/hex_resolution_comparison.jpg)

<br>

## highway2vec
![](images/method_framework_v2.png)
### Autoencoder
![](images/autoencoder_v2.png)
### Aggregation
![](images/feature_aggregation.png)

<br>

## Results
### <b>Typology</b>
|  | Color | Description |
| ---: | ----------- | ---- |
| 0 | blue | high-capacity regions containing arterial roads |
| 1 | light blue | residential, paved regions with good quality of road infrastructure |
| 2 | orange | residential, unpaved regions with low quality of road infrastructure |
| 3 | light orange | regions complementing main road network |
| 4 | green | high-capacity, high-speed regions and bypasses |
| 5 | light green | estate regions and connectors |
| 6 | red | motorways |
| 7 | light red | traffic collectors and connectors |


### <b>Microregions</b>
| City | Typology | 
| --- | ----------- | 
| Bydgoszcz | ![Bydgoszcz](images/Bydgoszcz_hexagons.png) |
| Cracow | ![Cracow](images/Krakow_hexagons.png) |
| Poznan | ![Poznan](images/Poznan_hexagons.png) |
| Tricity | ![Trójmiasto](images/Trojmiasto_hexagons.png) |
| Warsaw | ![Warszawa](images/Warszawa_hexagons.png) |
| Wroclaw | ![Wrocław](images/Wroclaw_hexagons.png) |

### <b>Latent Space</b>
t-SNE
![TSNE](images/tsne_hexes.png)

| City | Latent space projected into RGB | 
| --- | ----------- | 
| Bydgoszcz | ![Bydgoszcz](images/Bydgoszcz.png) |
| Cracow | ![Cracow](images/Kraków.png) |
| Poznan | ![Poznan](images/Poznań.png) |
| Tricity | ![Trójmiasto](images/Trójmiasto.png) |
| Warsaw | ![Warszawa](images/Warszawa.png) |
| Wroclaw | ![Wrocław](images/Wrocław.png) |

### <b>Operations in latent space</b>

| Summand | Summand | Result |
| --- | ----------- | --- |
| High-traffic region containing a bridge | Residential region | Residential area next to high-traffic roads |
| ![](images/hex_891e2047243ffff_map.jpg) | ![](images/hex_891e2045483ffff_map.jpg) | ![](images/hex_891e24aa0bbffff_map.jpg)

<br>

## Appendix
### City feature occurance
![](images/city_feature_occurrence.svg)