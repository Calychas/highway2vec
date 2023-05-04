![](images/Krakow_hexagons.png)

# highway2vec
<b>Kacper Leśniara and Piotr Szymański</b>

<i>Representing OpenStreetMap microregions with respect to their road network characteristics</i>

Paper: https://github.com/Calychas/highway2vec/blob/master/SIGSPATIAL_2022_paper_262.pdf

This is a companion repository to the paper accepted at The 5th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI ’22).

## 📝 Repository status
This Github repository is no longer maintained.
If you're interested in highway2vec or geospatial data in general, we encourage you to take a look at [Spatial Representations for AI](https://github.com/srai-lab/srai).  
It implements highway2vec along with other models and utilities for working with geospatial data. The new highway2vec pipeline, which uses SRAI and Kedro is available [here](https://github.com/Calychas/highway2vec_remaster). If you have any feature request or a bug to report, feel free to open an issue in [the SRAI repo](https://github.com/srai-lab/srai/issues).

Reference:
```
Kacper Leśniara and Piotr Szymański. 2022. highway2vec - representing OpenStreetMap microregions with respect to their road network charac- teristics. In The 5th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI ’22) (GeoAI ’22), November 1, 2022, Seattle, WA, USA. ACM, New York, NY, USA, 12 pages. https://doi.org/10. 1145/3557918.3565865
```

## Steps to run
* `pip install -r requirements.txt`
* `python scripts/download_and_preprocess_data.py`<br>
    This will download the data for selected cities and preprocess it (see `data/generated`).
* `python scripts/generate_dataset.py`<br>
    This will generate dataset from the preprocessed data (see `data/features`).
* Run `notebooks/vis_data.ipynb`, which will generate data visualizations (see `reports/figures`)
* Run `notebooks/autoencoder.ipynb`, which will train the model run the inference (see `data/runs/<run_name>`).
* Run `notebooks/vis_ae.ipynb`, which will generate the analyses and visualizations of the generated embeddings (see `data/runs/<run_name>/vis`).

### Final run used in the paper is available [here](https://drive.google.com/file/d/1f8UQDkxDGj9h9ic_RANRiI352aS-zfiZ/view?usp=sharing)
