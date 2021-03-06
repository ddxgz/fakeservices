# fitbit:
# https://p4-service-fitbit-f642omuzga-uc.a.run.app/1/user/-/activities/steps/date/2018-01-01/2018-01-03/
# ihealth:
# https://p4-service-ihealth-f642omuzga-uc.a.run.app
# home:
# https://p4-service-home-f642omuzga-uc.a.run.app

import os
import time
from datetime import datetime
import asyncio
import logging
import random

import requests
import aiohttp
import numpy as np
import pandas as pd
from typing import List, Tuple

from fakeservices import config, fitbit_app, ihealth_app
import azure_utils

logger = logging.getLogger(__name__)
# logger.setLevel(logging.In)
handler = logging.FileHandler(filename='requests.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)

SERVICE_MAP = {'fitbit': ['steps']}
GOOGLE_KEY = config.CREDENTIALS['google_search_api_key']
GOOGLE_CX = config.CREDENTIALS['search_engine_id']
TMDB_KEY = config.CREDENTIALS['tmdb_api_key']
CITIES = [
    'stockholm', 'gothenburg', 'paris', 'london', 'tokyo', 'shanghai',
    'new york', 'hongkong', 'singapore', 'berlin'
]


def get_url(name: str,
            host: str,
            resource: str = 'steps',
            start_date: str = '2018-01-01',
            end_date: str = '2018-01-03'):
    if host == 'gcloud':
        base = config.SERVICE_ENDPOINT[name]
    elif host == 'azure':
        base = config.AZURE_SERVICE_ENDPOINT[name]
    elif host == 'vultr':
        base = config.VULTR_SERVICE_ENDPOINT[name]
    else:
        host = 'gcloud'
        base = config.SERVICE_ENDPOINT[name]

    if name == 'fitbit':
        res_path = f'/1/user/-/activities/{resource}/date/{start_date}/{end_date}/'
    elif name == 'ihealth':
        res_path = f'/openapiv2/application/{resource}.json?start_date={start_date}&end_date={end_date}'
    elif name == 'phr':
        res_path = f'/Observation?start_date={start_date}&end_date={end_date}'
    elif name == 'home':
        res_path = '/environment'
    else:
        res_path = '/environment'

    return base + res_path


def gen_requests(provider: str) -> Tuple[str, List[Tuple[str, dict, str]]]:
    """generate a list of requests to be performed

    A list of tuples of (url, content_type, service_name)
    """
    pairs = []
    content_types = ['application/json', 'application/ld+json']
    start_date = '2019-01-01'

    start = pd.Timestamp(start_date)
    end = start + pd.offsets.Day(np.random.randint(1, 60))
    end_date = end.date()

    pairs.append((get_url('home', provider, resource='environment'), {
        'Content-Type': 'text/turtle'
    }, 'home'))

    fitbit_res_types = list(fitbit_app.res_tag.keys())
    fitbit_res_type = np.random.choice(range(0, len(fitbit_res_types)))
    json_content_type = np.random.choice(content_types)
    fitbit_url = get_url('fitbit',
                         provider,
                         resource=fitbit_res_types[fitbit_res_type],
                         start_date=start_date,
                         end_date=end_date)
    pairs.append((fitbit_url, {'Content-Type': json_content_type}, 'fitbit'))

    ihealth_res_types = list(ihealth_app.resource_data_key.keys())
    ihealth_res_type = np.random.choice(ihealth_res_types)
    ihealth_content_type = np.random.choice(content_types)
    ihealth_url = get_url('ihealth',
                          provider,
                          resource=ihealth_res_type,
                          start_date=start_date,
                          end_date=end_date)
    pairs.append((ihealth_url, {'Content-Type': json_content_type}, 'ihealth'))

    pairs.append((get_url('phr',
                          provider,
                          start_date=start_date,
                          end_date=end_date), {
                              'Content-Type': 'application/fhir+turtle'
                          }, 'phr'))

    return 'health services', pairs


def process_results(results,
                    name,
                    start_total,
                    spent_total,
                    req_location='Stockholm',
                    req_bredband='ComHem 100M/100M'):
    """
    data to record:
    - req_start
    - req_end/req_duration
    - service_name
    - resource_type
    - content_type
    - content_length
    - cloud provider
    - req_location
    - req_bredband

    example result item: {
            'status': status,
            # 'text': text,
            'request_at': start,
            'spent': spent,
            'content_type': resp_headers.get('Content-Type'),
            'content_length': resp_headers.get('Content-Length'),
            'bytes_len': utf8len(text),
            'service_name': service_name,
            'url': url,
        }
    """
    df = pd.DataFrame(results)
    df['req_total_start_at'] = pd.Series(
        np.repeat(start_total, repeats=len(results)))
    df['req_total_spent'] = pd.Series(
        np.repeat(spent_total, repeats=len(results)))
    df['req_location'] = pd.Series(
        np.repeat(req_location, repeats=len(results)))
    df['req_bredband'] = pd.Series(
        np.repeat(req_bredband, repeats=len(results)))
    # print(df)

    if not os.path.exists('results'):
        os.mkdir('results')

    dirname = 'results'
    filename = f'{name}_{start_total}.csv'
    csv_file = os.path.join(dirname, filename)
    df.to_csv(csv_file)
    azure_utils.upload_file_datalake(filename,
                                     dirname,
                                     to_path='req-results/results/pi')


def gen_common_service_requests(query_cities=CITIES):
    query = random.choice(query_cities)

    urls = {
        # 'google search': f'https://google.se/search?q={query}',
        'google search': f'https://google.com/search?q={query}',
        'reddit search': f'https://www.reddit.com/search/?q={query}',
        'reddit': f'https://www.reddit.com/',
        # yelp
        # f'https://www.yelp.se/search?find_desc=Restauranger&find_loc=Stockholm',
        'yelp restaurant search':
        f'https://www.yelp.com/search?find_desc=Restauranger&find_loc={query}',
        'web archive': f'https://archive.org/search.php?query={query}',
        'imdb': f'https://www.imdb.com/find?q={query}',
        'tmdb': f'https://www.themoviedb.org/search?query={query}',
    }

    headers = {}
    return 'common services', [(req_url, headers, name)
                               for name, req_url in urls.items()]


def gen_common_api_requests(query_cities=CITIES):
    query = random.choice(query_cities)

    urls = {
        # yelp
        # f'https://api.yelp.com/v3/businesses/search?term={query}'

        # https://developers.google.com/custom-search/v1/using_rest#response_data
        'google search api':
        f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_KEY}&cx={GOOGLE_CX}&q={query}',
        'duck api':
        f'https://api.duckduckgo.com/?q={query}&format=json',

        ## Teleport public APIs https://developers.teleport.org/api/
        'teleport api':
        f'https://api.teleport.org/api/cities/?{query}',

        ## The Internet Archive (the “Archive”) https://archive.readme.io/docs/getting-started
        'web archive api':
        f'https://archive.org/advancedsearch.php?q={query}&output=json&rows=100',
        # f'https://archive.org/wayback/available?url={query}',

        # https://www.mediawiki.org/wiki/API:Search
        'wikipedia api':
        f'https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}',
        'tmdb api':
        f'https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={query}',
    }

    headers = {}
    return 'common apis', [(req_url, headers, name)
                           for name, req_url in urls.items()]


def utf8len(s):
    return len(s.encode('utf-8'))


async def fetch(session, url, headers, service_name):
    start = time.time()
    # print(f'start:{start}')
    try:
        async with session.get(url, headers=headers) as resp:
            status = resp.status
            text = await resp.text()
            spent = time.time() - start
            # print(f'spent: {spent}')
            resp_headers = resp.headers
    except aiohttp.client_exceptions.ClientConnectorError as e:
        logger.error(f'error client exception when call {url}')
        return {
            'status': 999,
            # 'text': text,
            'request_at': start,
            'spent': 999,
            'content_type': 'client exception',
            'content_length': 'client exception',
            'bytes_len': 0,
            'service_name': service_name,
            'url': url,
        }
    else:
        return {
            'status': status,
            # 'text': text,
            'request_at': start,
            'spent': spent,
            'content_type': resp_headers.get('Content-Type'),
            'content_length': resp_headers.get('Content-Length'),
            'bytes_len': utf8len(text),
            'service_name': service_name,
            'url': url,
        }


async def req_services(url_headers: List[Tuple[str, dict, str]]):
    async with aiohttp.ClientSession() as sess:
        # for i in range(10):
        # start = time.time()
        results = await asyncio.gather(*[
            fetch(sess, url=pair[0], headers=pair[1], service_name=pair[2])
            for pair in url_headers
        ])
        # spent = time.time() - start

        # print(f'req time: {spent}')
        # return spent

        # print(txt)
        return results


def pin_cloudrun(reqs):
    logger.info(f'pin cloud run {[pair[2] for pair in reqs[1]]}')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(req_services(reqs[1]))


def run():
    """
    1) generate list of parameters for requests
    2) async requests
    3) gather results and persist
    """
    try:
        pin_cloudrun(gen_requests('gcloud'))
        pin_cloudrun(gen_requests('azure'))
    except:
        logger.error('pin cloud run failed, wait some time to pin again.')
        time.sleep(10 * 60)
        pin_cloudrun(gen_requests())

    time.sleep(10)

    req_list = []
    req_list.append(gen_common_api_requests())
    req_list.append(gen_common_service_requests())
    req_list.append(gen_requests('gcloud'))
    req_list.append(gen_requests('azure'))
    req_list.append(gen_requests('vultr'))
    random.shuffle(req_list)

    for name, reqs in req_list:
        loop = asyncio.get_event_loop()
        start = time.time()
        results = loop.run_until_complete(req_services(reqs))
        spent = time.time() - start

        # logger.info(f'total time spent: {spent}')
        # print(results)
        process_results(results,
                        name=name,
                        start_total=start,
                        spent_total=spent)

        logger.info(f'Processed result of [{name}] | '
                    f'total time spent [{spent:.4f}] | '
                    f'started at [{datetime.fromtimestamp(start)}]')


if __name__ == '__main__':
    try:
        while True:
            run()
            time.sleep(0.7 * 60 * 60)
    except:
        logger.error('Error while run(), wait some time to try again.')
        time.sleep(10 * 60)
        while True:
            run()
            time.sleep(1 * 60 * 60)

    # print(config.CREDENTIALS['google_search_api_key'])