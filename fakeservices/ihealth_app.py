import json
import time
from datetime import datetime, timedelta, tzinfo
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


class iHealthModel:
    def __init__(self,
                 resource_path='glucose',
                 base_date='2018-01-01',
                 end_date='2018-01-5',
                 userid=app.secret_key):
        self.resource_path = resource_path
        self.base_date = base_date
        self.end_date = end_date
        self.userid = userid
        # self.data = self.generate()
        self.res_data_key = {
            'glucose': ('BGDataList', 'gen_glucose', 'BGUnit')
        }
        self.data_key = self.res_data_key[resource_path][0]
        self.gen_func = getattr(self, self.res_data_key[resource_path][1])
        self.unit_key = self.res_data_key[resource_path][2]

    @property
    def data(self):
        return self.generate()

    def generate(self):
        dates = pd.date_range(start=self.base_date,
                              end=self.end_date,
                              freq='D')
        logs = []
        for d in dates:
            logs += self.gen_func(d)

        resp = {
            self.data_key: logs,
            self.unit_key: 0,
            'CurrentRecordCount': len(logs),
            'PageNumber': 1,
            'RecordCount': len(logs),
        }
        return resp

    def json(self):
        return json.dumps(self.data)

    def gen_glucose(self, date):
        mgdls = np.random.normal(170, 30, 3)
        mgdls.sort()

        dinner_situations = {
            'Before_breakfast': 8,
            'Before_lunch': 12,
            'Before_bed': 22
        }

        drug_situation = 'After_taking_pills'

        measures = []
        for bg, (din, hour) in zip(mgdls, dinner_situations.items()):
            m_date = int(
                datetime.timestamp(
                    # datetime.fromtimestamp(date) +
                    date + timedelta(hours=np.random.normal(hour, 0.6))))
            measures.append({
                'BG': round(bg, 1),
                'DataID': str(uuid.uuid4()),
                'DinnerSituation': din,
                'DrugSituation': drug_situation,
                'MDate': m_date,
                'uderid': self.userid,
                'Note': 'nothing',
                'LastChangeTime': m_date,
                "DataSource": "FromDevice",
                'TimeZone': '+0200'
            })

        return measures


# user-id, The encoded ID of the user. Use "-" (dash) for current logged-in user.
# support only date range, the additional time information is ignored
@app.route('/openapiv2/application/<resource_path>.json', methods=['GET'])
def activities(resource_path):
    if request.method == 'GET':
        start = datetime.timestamp(datetime.now() - timedelta(days=7))
        now = datetime.timestamp(datetime.now())
        start_time = int(request.args.get('start_time', start))
        end_time = int(request.args.get('end_time', now))
        start_date = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')

        activity = iHealthModel(resource_path, start_date, end_date)
        logger.debug(f'data: {activity}')
        return jsonify(activity.data)


@app.route('/1/user/-/foods/log/<resource_path>/date/<base_date>/<end_date>/',
           methods=['GET'])
def foods_log(resource_path, base_date, end_date):
    if request.method == 'GET':
        activity = FitbitModel('foods/log', resource_path, base_date, end_date)
        logger.debug(f'data: {activity}')
        return jsonify(activity.data)