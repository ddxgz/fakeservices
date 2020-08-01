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

from . import home_service
# from . import utils

# logger = utils.mylogger(__name__)

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.debug = False
wsgiapp = app.wsgi_app

_sys_name = 'BobHomeEnv'
_sensors_hu = home_service.HumiditySensor(f'{_sys_name}/SensorHumidity')
_sensors_te = home_service.TemperatureSensor(
    f'{_sys_name}/TemperatureHumidity')

HOME_SYS = home_service.System(_sys_name)
HOME_SYS.add_sensor(_sensors_te)
HOME_SYS.add_sensor(_sensors_hu)
HOME_SYS.init_observations(num=500, days_back=500 / 10 + 5)


# support only date range, the additional time information is ignored
@app.route('/environment', methods=['GET'])
def environment():
    if request.method == 'GET':
        graph = HOME_SYS.current_obs_graph_str()

        # logger.debug(f'data: {graph}')
        return (graph, 200, {'Content-Type': 'text/turtle'})
