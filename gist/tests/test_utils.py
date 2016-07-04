import unittest
from .. import utils


class UtilTest(unittest.TestCase):
    def test_json_to_dict(self):
        fp = open("examples/sst_example.json", "r")
        d = utils.json_to_dict(fp)
        self.assertIsInstance(d, dict)


if __name__ == '__main__':
    unittest.main()
