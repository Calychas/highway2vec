# highway2vec
<b>Kacper Leśniara and Piotr Szymański</b>

<i>Representing OpenStreetMap microregions with respect to their road network characteristics</i>

![](images/Krakow_hexagons.png)

This is a companion repository to the paper accepted at The 5th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI ’22).

Reference:
```
Kacper Leśniara and Piotr Szymański. 2022. highway2vec - representing OpenStreetMap microregions with respect to their road network charac- teristics. In The 5th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI ’22) (GeoAI ’22), November 1, 2022, Seattle, WA, USA. ACM, New York, NY, USA, 12 pages. https://doi.org/10. 1145/3557918.3565865
```

# Steps to run
* `pip install -r requirements.txt`
* `python scripts/download_and_preprocess_data.py`<br>
    This will download the data for selected cities and preprocess it (see `data/generated`).
* `python scripts/generate_dataset.py`<br>
    This will generate dataset from the preprocessed data (see `data/features`).
* Run `notebooks/vis_data.ipynb`, which will generate data visualizations
* Run `notebooks/autoencoder.ipynb`, which will train the model run the inference (see `runs/<run_name>`).
* Run `notebooks/vis_ae.ipynb`, which will generate the analyses and visualizations of the generated embeddings (see `runs/<run_name>/vis`).

## Final run used in the paper is available [here](https://drive.google.com/file/d/1f8UQDkxDGj9h9ic_RANRiI352aS-zfiZ/view?usp=sharing)