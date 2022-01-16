SHELL = /usr/bin/env bash

# Data
data: data_dir geo_data

data_dir:
	mkdir -p data

geo_data:
	wget -O ./data/admin_units_pl.geojson https://capap.gugik.gov.pl/api/repo/publ/gugik/data/jednostki-administracyjne-f5cnk/file/typ-podpowiedz-nazwa-teryt-parentid-geojson.geojson/get

# Environment
requirements:
	pip install -r requirements.txt

# Linters
format: black isort

black:
	black --line-length 120 .

isort:
	isort --settings-path setup.cfg .
