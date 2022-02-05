# way-to-school
The project involves obtaining the necessary data and conducting geospatial analyzes regarding the distribution and availability of schools at various levels of education in Poland.

## Setting up local environment

Create and activate virtual environment

```shell
python -m venv venv
source venv/bin/activate
```

Install project dependencies

```shell
# Assuming you've activated your project's virtual environment
make requirements
```

### Additional tools that may be needed during the development
### [pip-tools](https://github.com/jazzband/pip-tools)
```shell
pip install pip-tools
```

## Data

Download and preprocess the necessary data

```shell
make data
```
