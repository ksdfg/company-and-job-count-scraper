#!/usr/bin/env bash

set +x

# Run the docker container
docker run -it -v ./data:/data --env-file .env linkedin-scraper