# BentoML Boilerplate

BentoML Boilerplate is a template for building model serving systems using BentoML.


## Dependencies

We haveIt has been confirmed that this project works well in Python 3.9.5 version.  
Below is a list of versions of major libraries that have been confirmed to work well.

- BentoML==0.13.1
- tensorflow==2.8.0
- torch==1.11.0
- scikit-learn==1.0.2


## Installation

Install the dependencies recorded in requirements.txt

```shell
$ pip install -r requirements.txt 
```


## Training a Model

Run train.py to train the model.  
To specify a project, fill the --project option with its name.

```shell
$ python train.py --project=<PROJECT_NAME>

# example
$ python train.py --project=iris_sklearn
$ python train.py --project=mnist_tf
$ python train.py --project=mnist_torch
```

## Packing the model to BentoService

Run packer.py to pack the model to the service.  
To specify a project, fill the --project option with its name.

```shell
$ python packer.py --project=<PROJECT_NAME>

# example
$ python packer.py --project=iris_sklearn
$ python packer.py --project=mnist_tf
$ python packer.py --project=mnist_torch
```


## Model Serving via REST API

To start a REST API model server locally with the IrisClassifier saved above, use the bentoml serve command followed by service name and version tag:

```shell
$ bentoml serve IrisSKClassifier:latest
```

Alternatively, use the saved path to load and serve the BentoML packaged model directly:
```shell
# Find the local path of the latest version IrisSKClassifier saved bundle
$ saved_path=$(bentoml get IrisSKClassifier:latest --print-location --quiet)
$ bentoml serve $saved_path
```


## Containerize Model API Server

One common way of distributing this model API server for production deployment, is via Docker containers. And BentoML provides a convenient way to do that.

If you already have docker configured, run the following command to build a docker container image for serving the IrisClassifier prediction service created above:

```shell
$ bentoml containerize IrisSKClassifier:latest -t iris-sklearn
```

Start a container with the docker image built from the previous step:

```shell
$ docker run -p 5000:5000 iris-sklearn:latest --workers=2
```

## Learning more about BentoML

Check out the [BentoML documentation](https://docs.bentoml.org/en/0.13-lts/) for more usage examples.
