import unittest
import io

from rdflib import URIRef
from rdflib.namespace import RDF

from fakeservices import home_service
from fakeservices.home_service import SOSA, QUDT


class Test_TestSystem(unittest.TestCase):
    def setUp(self):
        self.uid_sen = 'sensor1'
        self.sen = home_service.HumiditySensor(self.uid_sen)
        self.uid_sen2 = 'sensor2'
        self.sen2 = home_service.HumiditySensor(self.uid_sen2)
        self.uid_sys = 's1'
        self.sys = home_service.System(self.uid_sys, [self.sen, self.sen2])

    def test_graph_init(self):
        sys = home_service.System('s1')
        # for s, p, o in sys.graph.triples((None, RDF.type, None)):
        #     print(s, p, o)
        self.assertEqual(len(sys.graph), 1)

    def test_record_obs(self):
        for i in range(2):
            self.sys.record_obs()
        self.assertEqual(2, len(self.sys.sensors[0].observations))

    def test_graph_dump(self):
        sen = home_service.HumiditySensor('sensor1')
        sys = home_service.System('s1', [sen])
        sys.record_obs()
        out = io.BytesIO()
        # out = 'tmp/s1.ttl'
        sys.dump_rdf(out)
        # print(out.getvalue())
        self.assertIn(b's1', out.getvalue())
        self.assertIn(b'sensor1', out.getvalue())
        self.assertIn(b'Observation', out.getvalue())
        self.assertIn(b'Result', out.getvalue())


class Test_TestSensor(unittest.TestCase):
    def setUp(self):
        self.uid = 'sensor1'
        self.sen = home_service.HumiditySensor(self.uid)

    def test_record_obs(self):
        hs = home_service.HumiditySensor('hs1')
        s = home_service.System('s1', [hs])
        s.record_obs()
        # obs1 = s.obs[hs.uid]
        obs1 = s.sensors[0].observations
        self.assertEqual(len(obs1), 1)
        self.assertAlmostEqual(obs1[0]['value'], 40, delta=20)

    def test_add_observation(self):
        self.assertEqual(0, len(self.sen.observations))
        limit = 3
        self.sen.obs_limit = limit
        for i in range(limit):
            self.sen.add_observation({})
        self.assertEqual(limit, len(self.sen.observations))
        self.sen.add_observation({})
        self.assertEqual(limit, len(self.sen.observations))


class Test_TestHumiditySensor(unittest.TestCase):
    def setUp(self):
        self.uid = 'sensor1'
        self.sen = home_service.HumiditySensor(self.uid)

    def tearDown(self):
        pass

    def test_uid(self):
        self.assertEqual(self.sen.uid, self.uid)
        self.assertEqual(self.sen.uri, URIRef(self.uid))

    def test_type(self):
        type_ = 'Humidity'
        self.assertIn(type_, self.sen.obs_type)
        # self.assertEqual(sen.obs_type, URIRef(type_))

    def test_get_current(self):
        self.assertEqual(len(self.sen.observations), 0)
        obs = self.sen.get_current_obs()
        self.assertEqual(len(self.sen.observations), 1)
        # get last element in objects generator
        *_, result = self.sen.graph[URIRef(obs['@id']):SOSA.hasResult]
        *_, value_g = self.sen.graph[result:QUDT.numericValue:]
        self.assertEqual(obs['value'], value_g.toPython())

        self.assertAlmostEqual(self.sen.get_current_obs()[
                               'value'], 40, delta=20)

    def test__obs_id(self):
        self.assertEqual(self.sen._obs_id(), f'{self.uid}/Observation/1')


if __name__ == '__main__':
    unittest.main()
