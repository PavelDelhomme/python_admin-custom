from elasticsearch_dsl import connections
from os import getenv

elasticsearch_host = getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
connections.create_connection(hosts=[elasticsearch_host], timeout=20)
