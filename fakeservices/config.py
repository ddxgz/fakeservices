import os
import json

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#
# SERVER_DIR = os.path.join(BASE_DIR, 'nyapeking')
#
# RESTAURANT_JSON = os.path.join(SERVER_DIR, 'restaurant.json')

# [common]
# set logfilename if need log to file
#LOG_FILENAME = log
LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'DEBUG'
# # [article]
# ID_PREFIX = 'http://www.linkedinfo.co/id'
# INFO_PREFIX = 'http://www.linkedinfo.co/infos'
# TAG_PREFIX = 'http://www.linkedinfo.co/tags'
# # PERSON_PREFIX = 'http://www.linkedinfo.co/persons'
# CREATOR_PREFIX = 'http://www.linkedinfo.co/creator'
# AGGR_PREFIX = 'http://www.linkedinfo.co/aggregations'

# INFO_NAMESPACE = 'http://www.linkedinfo.co/vocab'
# STOREFN = os.path.abspath('./infosgraph.n3')

# # bugs for parsing jsonld with @context and @graph
# # STOREFN = os.path.abspath('./articles.jsonld')
# #storefn = '/home/simon/codes/film.dev/movies.n3'
# STOREURI = 'file://' + STOREFN

SERVICE_ENDPOINT = {
    'fitbit': 'https://p4-service-fitbit-f642omuzga-uc.a.run.app',
    'home': 'https://p4-service-home-f642omuzga-uc.a.run.app',
    'ihealth': 'https://p4-service-ihealth-f642omuzga-uc.a.run.app',
    'phr': 'https://p4-service-lhr-jena-phr-f642omuzga-uc.a.run.app',
}

AZURE_SERVICE_ENDPOINT = {
    'fitbit': 'http://p4-services-fitbit.northeurope.azurecontainer.io',
    'home':'http://p4-services-home.northeurope.azurecontainer.io',
    'ihealth':'http://p4-services-ihealth.northeurope.azurecontainer.io',
    'phr':'http://p4-services-lhr-jena-phr.northeurope.azurecontainer.io:8080',
}

with open('credentials.json', 'r') as f:
    CREDENTIALS = json.load(f)