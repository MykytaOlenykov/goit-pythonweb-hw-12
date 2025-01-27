#!/bin/bash

docker-compose -f docker-compose.yml up -d db_pythonweb

poetry run python src/main.py