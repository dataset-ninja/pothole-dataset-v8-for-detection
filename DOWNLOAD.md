Dataset **Pothole dataset v8 for detection** can be downloaded in Supervisely format:

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/1/O/De/PetX589MXf7NVEQ1alnouKCxYPSbZ79QB9MogwMZPt8cxr30Ksn0zu2Ci6j1O9dCErR9sbgaQOeAnwj6B51eokZngVTufpg3MOsmKsvB7URSMjhBUTWbr16KxWDO.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Pothole dataset v8 for detection', dst_path='~/dtools/datasets/Pothole dataset v8 for detection.tar')
```
The data in original format can be 🔗[downloaded here](https://www.dropbox.com/s/qvglw8pqo16769f/pothole_dataset_v8.zip?dl=1)