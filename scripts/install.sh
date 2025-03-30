#!/usr/bin/env bash

set +x

# Take input of all the API keys and tokens from user
echo
read -p "Enter the OpenAI API key: " OPENAI_API_KEY
echo
read -p "Enter the Coresignal API key: " CORESIGNAL_API_KEY
#echo
#read -p "Enter the Linkedin session cookie: " LI_AT_COOKIE

# Save the API keys in the .env file
echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
echo "CORESIGNAL_API_KEY=$CORESIGNAL_API_KEY" >> .env
#echo "LI_AT_COOKIE=$LI_AT_COOKIE" >> .env

# Build the docker image
echo
docker build -f Dockerfile -t linkedin-scraper .