Dataset **Pothole Dataset v8 for Detection** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/K/C/zA/oNdgu1exsJyigqTU8B1AFvVGWMRL5HBCEfuT24oexUNRZd0SM3P0UjI9tfyDo9VYwuzcHiROgUR7mzLuC2Y60gBw0x9zLfnt1SEclNUuOIbBu4ky3RBnf1ln35w1.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Pothole Dataset v8 for Detection', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](hhttps://www.kaggle.com/datasets/denisg04/pothle-detect/download?datasetVersionNumber=1)