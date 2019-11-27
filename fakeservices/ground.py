#%%
import pandas as pd
from datetime import datetime

dr = pd.date_range('2018-01-01', '2018-02-01', freq='D')
dr.strftime('%Y-%m-%d')
for d in dr:
    print(d.strftime('%Y-%m-%d'))

#%%
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

userid = 'aaa'
date = 1331554332

mgdls = np.random.normal(170, 30, 3)
mgdls.sort()

dinner_situations = {
    'Before_breakfast': 8,
    'Before_lunch': 12,
    'Before_bed': 22
}

drug_situation = 'After_taking_pills'

datas = []

for bg, (din, hour) in zip(mgdls, dinner_situations.items()):
    m_date = datetime.timestamp(
        datetime.fromtimestamp(date) +
        timedelta(hours=np.random.normal(hour, 0.6)))
    datas.append({
        'BG': round(bg, 1),
        'DataID': str(uuid.uuid4()),
        'DinnerSituation': din,
        'DrugSituation': drug_situation,
        'MDate': m_date,
        'uderid': userid,
        'Note': 'nothing',
        'LastChangeTime': m_date,
        'TimeZone': '+0200'
    })

print(datas)