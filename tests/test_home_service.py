import unittest
import io

from rdflib import URIRef
from rdflib.namespace import RDF

from fakeservices import home_service
from fakeservices.home_service import SOSA, QUDT


class Test_TestSystem(unittest.TestCase):
    def test_graph_init(self):
        sys = home_service.System('s1')
        # for s, p, o in sys.graph.triples((None, RDF.type, None)):
        #     print(s, p, o)
        self.assertEqual(len(sys.graph), 1)

    def test_graph_dump(self):
        sen = home_service.HumiditySensor('sensor1')
        sys = home_service.System('s1', [sen])
        sys.record_obs()
        # out = io.BytesIO()
        out = 'tmp/s1.ttl'
        sys.dump_rdf(out)
        # print(out.getvalue())
        # self.assertIn(b's1', out.getvalue())
        # self.assertIn(b'sensor1', out.getvalue())


class Test_TestSensor(unittest.TestCase):
    def test_record_obs(self):
        hs = home_service.HumiditySensor('hs1')
        s = home_service.System('s1', [hs])
        s.record_obs()
        obs1 = s.obs[hs.uid]
        self.assertEqual(len(obs1), 1)
        self.assertAlmostEqual(obs1[0]['value'], 40, delta=20)


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
