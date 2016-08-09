import os
import unittest
from .. import sst_simu


class SSTTest(unittest.TestCase):

    def test_time_convert_to_us(self):
        sim_time = sst_simu.convert_time_to_us("123", "us00")
        self.assertEqual(sim_time, 123)

    def test_compile_ember_output(self):
        sst_simu.compile_ember_output("gist/tests/ember_output/5k.log",
                                      "gist/tests/ember_output/")
        self.assertTrue(os.path.exists("gist/tests/ember_output/summary.csv"))

if __name__ == '__main__':
    unittest.main()

