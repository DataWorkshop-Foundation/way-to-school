SHELL = /usr/bin/env bash

# Environment
requirements:
	pip install -r requirements.txt

# Linters
format: black isort

black:
	black --line-length 120 .

isort:
	isort --settings-path setup.cfg .
