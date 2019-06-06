from typing import List
from datetime import datetime

from rdflib import Graph, Namespace, BNode, URIRef, Literal
from rdflib.namespace import RDF, XSD

from . import fake_sense_hat

IOT = Namespace('http://iotschema.org/')
SOSA = Namespace('http://www.w3.org/ns/sosa/')
SSN = Namespace('http://www.w3.org/ns/ssn/')
QUDT = Namespace('http://qudt.org/1.1/schema/qudt#')
QUDT_UNIT = Namespace('http://qudt.org/1.1/vocab/unit#')


class Sensor:
    def __init__(self, uid, obs_type, system=None):
        self.uid = uid
        self.uri = URIRef(uid)
        self.__type = obs_type
        self._system = ''
        if system:
            self.system = system
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

    def _obs_id(self):
        return f'{self.uid}/Observation/{len(self.observations)+1}'

    def _obs_uri(self):
        return URIRef(self._obs_id())

    def _result_node(self, obs: dict) -> BNode:
        node = BNode()
        self.graph.add((node, RDF.type, QUDT.QuantityValue))
        self.graph.add((node, QUDT.unit, QUDT_UNIT.DegreeCelsius))
        self.graph.add((node, QUDT.numericValue, Literal(
            obs['value'], datatype=XSD.double)))
        return node


class HumiditySensor(Sensor):
    def __init__(self, uid):
        super().__init__(uid, IOT.Humidity)

    def get_current_obs(self):
        obs_id = self._obs_id()
        obs_uri = self._obs_uri()

        self.graph.add((self.uri, SOSA.madeObservation, obs_uri))
        self.graph.add((obs_uri, RDF.type, SOSA.Observation))
        self.graph.add((obs_uri, SOSA.observedProperty, URIRef(self.system)))
        self.graph.add((obs_uri, SOSA.madeBySensor, self.uri))
        time_now = datetime.now()
        resultTime = f'{(time_now.strftime("%Y-%m-%dT%H-%M-%S"))}+02:00'
        self.graph.add(
            (obs_uri, SOSA.resultTime, Literal(time_now, datatype=XSD.dateTime)))

        obs = {
            '@id': obs_id,
            'value': self.sensor.get_humidity(),
            'unit': 'qudt-unit-1-1:DegreeCelsius',
            'type': 'qudt-q-q:QuantityValue',
            'result_time': resultTime,
        }
        self.observations.append(obs)
        # TODO result to graph
        self.graph.add((obs_uri, SOSA.hasResult, self._result_node(obs)))
        return obs


class System:
    def __init__(self, uid, sensors: List[Sensor] = []):
        self.uid = uid
        self.uri = URIRef(uid)
        self.graph = Graph()
        self.graph.add((self.uri, RDF.type, SSN.System))
        self.__bind_namespaces()

        self.sensors = []  # type: List[Sensor]
        if len(sensors) > 0:
            for s in sensors:
                self.add_sensor(s)
        self.obs = {}  # type: dict

    def add_sensor(self, sensor: Sensor):
        self.sensors.append(sensor)
        sensor.system = self.uid
        self.graph.add((self.uri, SSN.hasSubSystem, sensor.uri))

    def load(self, obj_in):
        pass

    def dump_rdf(self, out, format='turtle'):
        for s in self.sensors:
            # s.graph.serialize(out, format=format)
            self.graph += self.graph + s.graph
        self.graph.serialize(out, format=format)

    def record_obs(self):
        for sensor in self.sensors:
            if not self.obs.get(sensor.uid):
                self.obs[sensor.uid] = []

            self.obs[sensor.uid].append(sensor.get_current_obs())
            # TODO to add
            # self.graph.add((obs_id, SOSA.observedProperty, obs_id))

    def run(self, obs_interval=10):
        pass

    def __bind_namespaces(self):
        self.graph.bind("ssn", SSN)
        self.graph.bind("sosa", SOSA)
        self.graph.bind("iot", IOT)
        self.graph.bind("qudt-1-1", QUDT)
        self.graph.bind('qudt-unit-1-1', QUDT_UNIT)


if __name__ == '__main__':
    hs = HumiditySensor('hs')
    print(hs.get_current_obs())
