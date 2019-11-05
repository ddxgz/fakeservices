import json
import time
import uuid
from functools import partial

from flask import Flask, jsonify, request, session, g, redirect, url_for, abort, \
    render_template, flash, send_from_directory
# import requests
import numpy as np
import pandas as pd

from . import utils

logger = utils.mylogger(__name__)

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


class FitbitModel:
    def __init__(self,
                 activity='activities',
                 resource_path='steps',
                 base_date='2018-01-01',
                 end_date='2018-01-5'):
        self.activity = activity
        self.resource_path = resource_path
        self.base_date = base_date
        self.end_date = end_date
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
            logs.append({
                'dateTime': d.strftime('%Y-%m-%d'),
                'value': int(abs(random_datum[self.resource_path]())),
            })

        return {f'{self.activity}-{self.resource_path}': logs}

    def json(self):
        return json.dumps(self.data)


# user-id, The encoded ID of the user. Use "-" (dash) for current logged-in user.
@app.route('/1/user/-/activities/<resource_path>/date/<base_date>/<end_date>/',
           methods=['GET'])
def activities(resource_path, base_date, end_date):
    if request.method == 'GET':
        activity = FitbitModel('activities', resource_path, base_date,
                               end_date)
        logger.debug(f'data: {activity}')
        return jsonify(activity.data)


@app.route('/1/user/-/foods/log/<resource_path>/date/<base_date>/<end_date>/',
           methods=['GET'])
def foods_log(resource_path, base_date, end_date):
    if request.method == 'GET':
        activity = FitbitModel('foods/log', resource_path, base_date, end_date)
        logger.debug(f'data: {activity}')
        return jsonify(activity.data)