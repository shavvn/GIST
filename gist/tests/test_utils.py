import unittest
from .. import utils


class UtilTest(unittest.TestCase):
    def test_json_to_dict(self):
        fp = open("examples/sst_example.json", "r")
        d = utils.json_to_dict(fp)
        self.assertIsInstance(d, dict)

    def test_logger_debug(self):
        arg_parser = utils.ArgParser("-d")
        logger = arg_parser.get_logger()
        logger.debug("you should see this")
        level = logger.level
        self.assertEqual(level, 10)


if __name__ == '__main__':
    unittest.main()
