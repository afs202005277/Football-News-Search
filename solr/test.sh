#!/bin/bash

sudo docker stop pri-solr-v3
# This script expects a container started with the following command.
sudo docker run --rm -p 8985:8983 --name pri-solr-v3 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v3
docker cp ./pri_synonyms.txt pri-solr-v3:/var/solr/data/news_articles_v3/conf


sleep 5
echo "Running on port 8983:v1 and 8984:v2"

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema3.json" \
    http://localhost:8985/solr/news_articles_v3/schema


# Populate collection using mapped path inside container.
sudo docker exec -it pri-solr-v3 bin/post -c news_articles_v3 /data/data.json
