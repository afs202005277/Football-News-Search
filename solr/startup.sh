#!/bin/bash

# This script expects a container started with the following command.
docker run --rm -p 8983:8983 --name pri-solr -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles

sleep 5
echo "Running on port 8983"

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema.json" \
    http://localhost:8983/solr/news_articles/schema

# Populate collection using mapped path inside container.
docker exec -it pri-solr bin/post -c news_articles /data/data.json

