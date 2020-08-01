import json
import time
import uuid
from functools import partial

from flask import Flask, jsonify, request, session, g, redirect, url_for, abort, \
    render_template, flash, send_from_directory
# import requests
import numpy as np
import pandas as pd

# from . import utils

# logger = utils.mylogger(__name__)

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.debug = False
wsgiapp = app.wsgi_app

random_datum = {
    'steps': partial(np.random.normal, 5000, 5000),
    'calories': partial(np.random.normal, 1650, 200),
    'caloriesIn': partial(np.random.normal, 3000, 200),
    'water': partial(np.random.normal, 800, 200),
}

res_tag = {
    'steps': 'schema:steps',
    'calories': 'schema:calories',
    'caloriesIn': 'schema:calories',
    'water': 'saref:Water',
}


class FitbitModel:
    def __init__(self,
                 activity='activities',
                 resource_path='steps',
                 base_date='2018-01-01',
                 end_date='2018-01-5',
                 require_annotation=False):
        self.activity = activity
        self.resource_path = resource_path
        self.base_date = base_date
        self.end_date = end_date
        self.require_annotation = require_annotation
        # self.data = self.generate()

    @property
    def data(self):
        return self.generate()

    def generate(self):
        dates = pd.date_range(start=self.base_date,
                              end=self.end_date,
                              freq='D')
        logs = []
        for d in dates:
            item = {
                'dateTime': d.strftime('%Y-%m-%d'),
                'value': int(abs(random_datum[self.resource_path]())),
            }
            if self.require_annotation:
                item['semrest:hasTag'] = {'@id': res_tag[self.resource_path]}
            logs.append(item)

        res_path = f'{self.activity}-{self.resource_path}'
        data = {res_path: logs}

        if self.require_annotation:
            data['@context'] = {
                "schema": "http://schema.org/",
                'dateTime': 'schema:dateTime',
                "semrest": "http://semrest.org/vocab#",
                'value': 'semrest:hasValue',
                res_path: 'semrest:dataItem',
                'saref': 'https://w3id.org/saref#',
            }

            data['@id'] = f"{res_path.replace('-', '/')}/{self.base_date}/{self.end_date}"
        return data

    def json(self):
        return json.dumps(self.data)


# user-id, The encoded ID of the user. Use "-" (dash) for current logged-in user.
@app.route('/1/user/-/activities/<resource_path>/date/<base_date>/<end_date>/',
           methods=['GET'])
def activities(resource_path, base_date, end_date):
    if request.method == 'GET':
        content_type = request.headers.get('Accept')
        # print(content_type)
        require_annotation = False
        if 'ld+json' in content_type:
            require_annotation = True
        activity = FitbitModel('activities', resource_path, base_date,
                               end_date, require_annotation=require_annotation)
        # logger.debug(f'data: {activity}')

        return jsonify(activity.data)


@app.route('/1/user/-/foods/log/<resource_path>/date/<base_date>/<end_date>/',
           methods=['GET'])
def foods_log(resource_path, base_date, end_date):
    if request.method == 'GET':
        content_type = request.headers.get('Accept')
        require_annotation = False
        if 'ld+json' in content_type:
            require_annotation = True
        activity = FitbitModel('foods/log', resource_path, base_date, end_date,
                               require_annotation=require_annotation)
        # logger.debug(f'data: {activity}')
        return jsonify(activity.data)
