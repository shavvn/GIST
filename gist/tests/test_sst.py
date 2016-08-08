import os
import unittest
from .. import sst_simu


class SSTTest(unittest.TestCase):

    def test_init(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        self.assertTrue(sst.param_list, "params not found!")

    def test_compile_ember_output(self):
        sst_simu.compile_ember_output("gist/tests/test_output/ember/5k.log",
                                      "gist/tests/test_output/ember/")
        self.assertTrue(os.path.exists("gist/tests/test_output/ember/summary.csv"))

if __name__ == '__main__':
    unittest.main()

