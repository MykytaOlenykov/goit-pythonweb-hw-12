#!/bin/bash

docker-compose -f docker-compose.yml up -d postgresdb
docker-compose -f docker-compose.yml up -d redisdb

export PYTHONPATH=$(pwd)
poetry run python src/main.py