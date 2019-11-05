from typing import List
import time
import io
from datetime import datetime, timedelta

from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, XSD
import numpy as np
import pysnooper

from . import fake_sense_hat
# import fake_sense_hat

IOT = Namespace('http://iotschema.org/')
SOSA = Namespace('http://www.w3.org/ns/sosa/')
SSN = Namespace('http://www.w3.org/ns/ssn/')
QUDT = Namespace('http://qudt.org/1.1/schema/qudt#')
QUDT_UNIT = Namespace('http://qudt.org/1.1/vocab/unit#')


class Sensor:
    def __init__(self, uid, obs_type, system=None, obs_limit=100):
        self.uid = uid
        self.uri = URIRef(uid)
        self.__type = obs_type
        self._system = ''
        if system:
            self.system = system
        self.obs_limit = obs_limit

        self.observations = []
        self.sensor = fake_sense_hat.SenseHat()

        self.graph = Graph()
        self.graph.add((self.uri, RDF.type, SSN.System))
        self.graph.add((self.uri, RDF.type, SOSA.Sensor))
        self.graph.add((self.uri, SOSA.observes, obs_type))

    @property
    def obs_type(self):
        return self.__type

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self, value):
        self._system = value

    def dump_rdf(self, out, format='turtle'):
        self.graph.serialize(out, format=format)

    # def set_system(self, system: str):
        # self._system = system

    def add_observation(self, obs):
        # not exceed the obs_limit
        if len(self.observations) >= self.obs_limit:
            self.observations.pop(0)
        self.observations.append(obs)

    def _add_obs_back(self, obs: dict, time_now=None) -> dict:
        obs_id = self._obs_id()
        obs_uri = self._obs_uri()

        self.graph.add((self.uri, SOSA.madeObservation, obs_uri))
        self.graph.add((obs_uri, RDF.type, SOSA.Observation))
        self.graph.add((obs_uri, SOSA.observedProperty, URIRef(self.system)))
        self.graph.add((obs_uri, SOSA.madeBySensor, self.uri))

        if not time_now:
            time_now = datetime.now()
        resultTime = f'{(time_now.strftime("%Y-%m-%dT%H-%M-%S"))}+02:00'
        self.graph.add(
            (obs_uri, SOSA.resultTime, Literal(time_now, datatype=XSD.dateTime)))

        self.graph.add((obs_uri, SOSA.hasResult, self._result_node(obs)))
        obs['@id'] = obs_id
        obs['result_time'] = resultTime
        return obs

    def _obs_id(self):
        return f'{self.uid}/Observation/{len(self.observations)+1}'

    def _obs_uri(self):
        return URIRef(self._obs_id())

    def _result_node(self, obs: dict) -> BNode:
        node = BNode()
        self.graph.add((node, RDF.type, URIRef(obs['type'])))
        # self.graph.add((node, RDF.type, QUDT.QuantityValue))
        # self.graph.add((node, QUDT.unit, QUDT_UNIT.DegreeCelsius))
        self.graph.add((node, QUDT.unit, obs['unit']))
        self.graph.add((node, QUDT.numericValue, Literal(
            obs['value'], datatype=XSD.double)))
        return node


class HumiditySensor(Sensor):
    def __init__(self, uid):
        super().__init__(uid, IOT.Humidity)

    def get_current_obs(self, time_now=None):
        obs = {
            # '@id': obs_id,
            'value': self.sensor.get_humidity(),
            # 'unit': 'qudt-unit-1-1:DegreeCelsius',
            'unit': QUDT_UNIT.Percent,
            'type': QUDT.QuantityValue,
            # 'type': 'qudt-q-q:QuantityValue',
            # 'result_time': resultTime,
        }
        obs = self._add_obs_back(obs, time_now)
        self.add_observation(obs)
        return obs


class TemperatureSensor(Sensor):
    def __init__(self, uid):
        super().__init__(uid, IOT.Temperature)

    def get_current_obs(self, time_now=None):
        obs = {
            'value': self.sensor.get_temperature(),
            'unit': QUDT_UNIT.DegreeCelsius,
            'type': QUDT.QuantityValue,
        }
        obs = self._add_obs_back(obs, time_now)
        self.add_observation(obs)
        return obs


class System:
    def __init__(self, uid: str = None, sensors: List[Sensor] = [],
                 file_or_bytesio=None):
        self.uid = uid if uid else ''
        self.uri = URIRef(uid) if uid else URIRef('')
        self.sensors = []  # type: List[Sensor]
        self.graph = Graph()
        self.__bind_namespaces()

        if file_or_bytesio:
            self.load(file_or_bytesio)
        else:
            self.graph.add((self.uri, RDF.type, SSN.System))

            if len(sensors) > 0:
                for s in sensors:
                    self.add_sensor(s)

        # self.obs = {}  # type: dict

    def add_sensor(self, sensor: Sensor):
        self.sensors.append(sensor)
        sensor.system = self.uid
        self.graph.add((self.uri, SSN.hasSubSystem, sensor.uri))

    def load(self, file_or_bytesio, format='turtle'):
        # self.graph = Graph()
        # data = b''
        # if isinstance(file_or_bytesio, str):
        #     with open(file_or_bytesio, 'r') as f:
        #         data = f.read()
        # elif isinstance(file_or_bytesio, bytes):
        #     data = file_or_bytesio
        # else:
        #     raise IOError
        # self.graph.parse(data=data, format=format)
        self.graph.parse(
            data=file_or_bytesio, format=format)
        uris = self.graph.subjects(RDF.type, SSN.system)
        uri = yield from uris
        print(f'uri from load: {uri}')
        self.uri = uri

    def dump_rdf(self, out, format='turtle'):
        for s in self.sensors:
            # s.graph.serialize(out, format=format)
            self.graph += self.graph + s.graph
        self.graph.serialize(out, format=format)

    def record_obs(self, time_now=None):
        for sensor in self.sensors:
            # if not self.obs.get(sensor.uid):
            #     self.obs[sensor.uid] = []

            # self.obs[sensor.uid].append(sensor.get_current_obs())
            # # TODO to add
            # # self.graph.add((obs_id, SOSA.observedProperty, obs_id))

            sensor.get_current_obs(time_now)

    # @pysnooper.snoop()
    def init_observations(self, num=100, days_back=5, obs_interval=100):
        time_now = datetime.now() - timedelta(days=days_back)
        for i in range(num):
            self.record_obs(time_now)
            interval = np.random.normal(obs_interval, obs_interval / 20)
            time_now += timedelta(seconds=interval)

    def run(self, obs_interval=10):
        for i in range(20):
            self.record_obs()
        while True:
            self.record_obs()
            time.sleep(obs_interval)

    def __bind_namespaces(self):
        self.graph.bind("ssn", SSN)
        self.graph.bind("sosa", SOSA)
        self.graph.bind("iot", IOT)
        self.graph.bind("qudt-1-1", QUDT)
        self.graph.bind('qudt-unit-1-1', QUDT_UNIT)


def generate_obs():
    num_sensors = range(1, 7)
    num_obs = range(13, 1000, 27)

    for num_sensor in num_sensors:
        for num_ob in num_obs:
            # print(num_sensor, num_ob)
            sys_name = f'AlexHomeEnv{num_sensor}_{num_ob}'

            sensors_hu = [HumiditySensor(
                f'{sys_name}/SensorHumidity{i}') for i in range(num_sensor)]
            sensors_te = [TemperatureSensor(
                f'{sys_name}/TemperatureHumidity{i}') for i in range(num_sensor)]

            sys = System(sys_name, sensors_hu + sensors_te)
            sys.init_observations(num=num_ob, days_back=num_ob / 10 + 5)
            sys.dump_rdf(f'tmp/{sys_name}.ttl')


if __name__ == '__main__':
    generate_obs()
