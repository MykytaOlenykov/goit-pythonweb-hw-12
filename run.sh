#!/bin/bash

docker-compose -f docker-compose.yml up -d db_pythonweb

export PYTHONPATH=$(pwd)
poetry run python src/main.py