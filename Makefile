SHELL = /usr/bin/env bash

# Data
data: data_dir geo_data school_coords school_csv

data_dir:
	mkdir -p data

geo_data:
	wget -O ./data/admin_units_pl.geojson https://capap.gugik.gov.pl/api/repo/publ/gugik/data/jednostki-administracyjne-f5cnk/file/typ-podpowiedz-nazwa-teryt-parentid-geojson.geojson/get

school_coords:
	gdown https://drive.google.com/uc?id=1S9jy4QY9jVlp0bSS_7YNqQ0_Lfz0LDvz -O data/school_data.jsonl

school_csv:
	gdown https://drive.google.com/uc?id=1lzLWaIvGB7r8nts63J71oZbIqgiiOhEd -O data/school_prep.csv

# Environment
requirements:
	source venv/bin/activate
	pip install -r requirements.txt

# Linters
format: black isort

black:
	black --line-length 120 .

isort:
	isort --settings-path setup.cfg .
