import os
import unittest
from .. import sst_simu


class SSTTest(unittest.TestCase):

    def test_init(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        self.assertTrue(sst.param_list, "params not found!")

       
if __name__ == '__main__':
    unittest.main()

