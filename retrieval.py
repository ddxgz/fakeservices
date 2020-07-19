# fitbit:
# https://p4-service-fitbit-f642omuzga-uc.a.run.app/1/user/-/activities/steps/date/2018-01-01/2018-01-03/
# ihealth:
# https://p4-service-ihealth-f642omuzga-uc.a.run.app
# home:
# https://p4-service-home-f642omuzga-uc.a.run.app

import time
import asyncio
import logging
import random

import requests
import aiohttp
import numpy as np
import pandas as pd
from typing import List, Tuple

from fakeservices import config, fitbit_app, ihealth_app

logger = logging.getLogger(__name__)
# logger.setLevel(logging.In)
handler = logging.FileHandler(filename='requests.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

SERVICE_MAP = {'fitbit': ['steps']}
GOOGLE_KEY = config.CREDENTIALS['google_search_api_key']
GOOGLE_CX = config.CREDENTIALS['search_engine_id']
TMDB_KEY = config.CREDENTIALS['tmdb_api_key']
CITIES = [
    'stockholm', 'gothenburg', 'paris', 'london', 'tokyo', 'shanghai',
    'new york', 'hongkong', 'singapore', 'berlin'
]


def get_url(name: str,
            resource: str = 'steps',
            start_date: str = '2018-01-01',
            end_date: str = '2018-01-03'):
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


def gen_requests() -> Tuple[str, List[Tuple[str, dict, str]]]:
    """generate a list of requests to be performed

    A list of tuples of (url, content_type, service_name)
    """
    pairs = []
    content_types = ['application/json', 'application/ld+json']
    start_date = '2019-01-01'

    start = pd.Timestamp(start_date)
    end = start + pd.offsets.Day(np.random.randint(1, 60))
    end_date = end.date()

    pairs.append((get_url('home', resource='environment'), {
        'Content-Type': 'text/turtle'
    }, 'home'))

    fitbit_res_types = list(fitbit_app.res_tag.keys())
    fitbit_res_type = np.random.choice(range(0, len(fitbit_res_types)))
    json_content_type = np.random.choice(content_types)
    fitbit_url = get_url('fitbit',
                         resource=fitbit_res_types[fitbit_res_type],
                         start_date=start_date,
                         end_date=end_date)
    pairs.append((fitbit_url, {'Content-Type': json_content_type}, 'fitbit'))

    ihealth_res_types = list(ihealth_app.resource_data_key.keys())
    ihealth_res_type = np.random.choice(ihealth_res_types)
    ihealth_content_type = np.random.choice(content_types)
    ihealth_url = get_url('ihealth',
                          resource=ihealth_res_type,
                          start_date=start_date,
                          end_date=end_date)
    pairs.append((ihealth_url, {'Content-Type': json_content_type}, 'ihealth'))

    pairs.append((get_url('phr', start_date=start_date, end_date=end_date), {
        'Content-Type': 'application/fhir+turtle'
    }, 'phr'))

    return 'health services', pairs


def process_results(results, name, start_total, spent_total):
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
    """
    pass


def gen_common_service_requests(query_cities=CITIES):
    query = random.choice(query_cities)
    # query = 'valley+forge+national+park'
    # query = 'https://lilianweng.github.io/lil-log/2020/04/07/the-transformer-family.html#sparse-attention-matrix-factorization-sparse-transformers'
    urls = {
        # 'google search': f'https://google.se/search?q={query}',
        'google search': f'https://google.com/search?q={query}',
        'reddit search': f'https://www.reddit.com/search/?q={query}',
        'reddit': f'https://www.reddit.com/',
        # yelp
        # f'https://www.yelp.se/search?find_desc=Restauranger&find_loc=Stockholm',
        'yelp restaurant search':
        f'https://www.yelp.com/search?find_desc=Restauranger&find_loc={query}',
        # f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_KEY}&cx={GOOGLE_CX}&q={query}',
        'web archive': f'https://archive.org/search.php?query={query}',
        'imdb': f'https://www.imdb.com/find?q={query}',
        'tmdb': f'https://www.themoviedb.org/search?query={query}',
        # f'https://api.duckduckgo.com/?q={query}&format=json',

        # https://www.mediawiki.org/wiki/API:Search
        # f'https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}'
    }

    headers = {}
    return 'common services', [(req_url, headers, name)
                               for name, req_url in urls.items()]


def gen_common_api_requests(query_cities=CITIES):
    # query = 'valley+forge+national+park'
    query = random.choice(query_cities)
    # query = 'https://lilianweng.github.io/lil-log/2020/04/07/the-transformer-family.html#sparse-attention-matrix-factorization-sparse-transformers'
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
    async with session.get(url, headers=headers) as resp:
        status = resp.status
        text = await resp.text()
        spent = time.time() - start
        # print(f'spent: {spent}')
        resp_headers = resp.headers
        return {
            'status': status,
            # 'text': text,
            'request_at': start,
            'spent': spent,
            'content_type': resp_headers.get('Content-Type'),
            'content_length': resp_headers.get('Content-Length'),
            'bytes_len': utf8len(text),
            'service': service_name,
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


def run():
    """
    1) generate list of parameters for requests
    2) async requests
    3) gather results and persist
    """
    req_list = []
    req_list.append(gen_common_api_requests())
    # url_headers_common = gen_common_service_requests()
    # url_headers_api = gen_common_api_requests()
    # url_headers_lhr = gen_requests()
    # print(url_headers)
    # req_list = [url_headers_common, url_headers_api, url_headers_lhr]
    print(req_list)
    random.shuffle(req_list)
    print(req_list)

    for name, reqs in req_list:
        loop = asyncio.get_event_loop()
        start = time.time()
        results = loop.run_until_complete(req_services(reqs))
        spent = time.time() - start

        print(f'total time: {spent}')
        print(results)
        process_results(results,
                        name=name,
                        start_total=start,
                        spent_total=spent)


if __name__ == '__main__':
    run()
    # print(config.CREDENTIALS['google_search_api_key'])