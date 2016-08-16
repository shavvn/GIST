import unittest
from .. import simulator


class SimulatorTest(unittest.TestCase):
    
    def setUp(self):
        self.p = {
            "foo": [1, 2, 3],
            "bar": {
                "duh": [4, 5],
                "huh": [6, 7, 8],
                "hmm": [9]
            }
        }
    
    def test_get_params_one_level(self):
        p_get = simulator.permute_params(self.p["bar"])
        self.assertIsInstance(p_get, list)
        self.assertEqual(len(p_get), 6)
        self.assertIn("duh", p_get[0])
        self.assertIn("huh", p_get[0])
        self.assertIn("hmm", p_get[0])
        
    def test_get_params_nested(self):
        p_get = simulator.permute_params(self.p)
        self.assertIsInstance(p_get, list)
        self.assertEqual(len(p_get), 18)
        self.assertIn("foo", p_get[0])
        self.assertIn("bar", p_get[0])
        self.assertIn("duh", p_get[0]["bar"])

    def test_get_params_from_list_of_dicts(self):
        p = {
            "ep": ["ember"],
            "work": [
                {
                    "type": "a",
                    "params": {
                        "bw": ["1GB/s", "2GB/s"],
                        "lat": ["1ns"]
                    }
                },
                {
                    "type": "b",
                    "params": {
                        "bw": ["3GB/s", "4GB/s"],
                        "lat": ["1ns"]
                    }
                }
            ]
        }
        p_get = simulator.permute_params(p)
        self.assertIsInstance(p_get, list)
        self.assertEqual(len(p_get), 4)

    def test_dump_param_header(self):
        header_gold = set(["configs", "foo", "duh", "huh", "hmm"])
        p_get = simulator.permute_params(self.p)
        header = ["configs", ]
        keys = simulator.get_keys_in_dict(p_get[0])
        header = set((keys+header))
        self.assertEqual(header, header_gold)

