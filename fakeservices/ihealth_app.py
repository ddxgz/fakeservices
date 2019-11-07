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
            'glucose': ('BGDataList', 'gen_glucose', 'BGUnit'),
            'weight': ('WeightDataList', 'gen_weight', 'WeightUnit'),
            'bp': ('BPDataList', 'gen_bp', 'BPUnit'),
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

    def gen_bp(self, date, freq=0.5):
        if np.random.random_sample() > freq:
            return []

        m_date = int(
            datetime.timestamp(date +
                               timedelta(hours=np.random.normal(8, 0.4))))

        hp = int(np.random.normal(125, 7, 1)[0])
        lp = int(np.random.normal(85, 5, 1)[0])
        hr = int(np.random.normal(80, 7, 1)[0])

        record = {
            'HP': hp,
            'LP': lp,
            'HR': hr,
            'DataID': str(uuid.uuid4()),
            'MDate': m_date,
            'uderid': self.userid,
            'Note': 'nothing',
            'LastChangeTime': m_date,
            "DataSource": "FromDevice",
            'TimeZone': '+0200'
        }
        return [record]

    def gen_weight(self, date, height=1.75, freq=0.3):
        if np.random.random_sample() > freq:
            return []

        m_date = int(
            datetime.timestamp(date +
                               timedelta(hours=np.random.normal(19, 0.6))))
        weight = round(np.random.normal(75, 2, 1)[0], 1)
        bmi = weight / (height * height)
        # boneval = np.random.normal(2, 1, 1)

        record = {
            'BMI': bmi,
            'WeightValue': weight,
            'DataID': str(uuid.uuid4()),
            'MDate': m_date,
            'uderid': self.userid,
            'Note': 'nothing',
            'LastChangeTime': m_date,
            "DataSource": "FromDevice",
            'TimeZone': '+0200'
        }
        return [record]

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
