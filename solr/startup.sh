#!/bin/bash

docker stop pri-solr-v1
docker stop pri-solr-v2
# This script expects a container started with the following command.
docker run --rm -p 8983:8983 --name pri-solr-v1 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v1
docker run --rm -p 8984:8983 --name pri-solr-v2 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v2

sleep 5
echo "Running on port 8983:v1 and 8984:v2"

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema1.json" \
    http://localhost:8983/solr/news_articles_v1/schema

# Populate collection using mapped path inside container.
docker exec -it pri-solr-v1 bin/post -c news_articles_v1 /data/data.json

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema2.json" \
    http://localhost:8984/solr/news_articles_v2/schema

# Populate collection using mapped path inside container.
docker exec -it pri-solr-v2 bin/post -c news_articles_v2 /data/data.json
