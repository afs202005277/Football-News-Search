#!/bin/bash

sudo docker stop pri-solr-v1
sudo docker stop pri-solr-v2
sudo docker stop pri-solr-v3
sudo docker stop pri-solr-v4
# This script expects a container started with the following command.
sudo docker run --rm -p 8983:8983 --name pri-solr-v1 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v1
sudo docker run --rm -p 8984:8983 --name pri-solr-v2 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v2
sudo docker run --rm -p 8985:8983 --name pri-solr-v3 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v3
sudo docker run --rm -p 8986:8983 --name pri-solr-v4 -v ${PWD}:/data -d solr:9.3 solr-precreate news_articles_v4
docker cp ./pri_synonyms.txt pri-solr-v3:/var/solr/data/news_articles_v3/conf
docker cp ./pri_synonyms.txt pri-solr-v4:/var/solr/data/news_articles_v4/conf

sleep 10
echo "Running on port 8983:v1, 8984:v2, 8985:v3, 8986:v4"

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema1.json" \
    http://localhost:8983/solr/news_articles_v1/schema

# Populate collection using mapped path inside container.
sudo docker exec -it pri-solr-v1 bin/post -c news_articles_v1 /data/data.json

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema2.json" \
    http://localhost:8984/solr/news_articles_v2/schema

# Populate collection using mapped path inside container.
sudo docker exec -it pri-solr-v2 bin/post -c news_articles_v2 /data/data.json

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema3.json" \
    http://localhost:8985/solr/news_articles_v3/schema

# Populate collection using mapped path inside container.
sudo docker exec -it pri-solr-v3 bin/post -c news_articles_v3 /data/data_embeddings.json

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema4.json" \
    http://localhost:8986/solr/news_articles_v4/schema

# Populate collection using mapped path inside container.
sudo docker exec -it pri-solr-v4 bin/post -c news_articles_v4 /data/data.json
