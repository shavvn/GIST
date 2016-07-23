import os
import unittest
from .. import sst_simu


class SSTTest(unittest.TestCase):
    def setUp(self):
        summary_csv = "gist/tests/test_output/summary.csv"
        if os.path.exists(summary_csv):
            os.remove(summary_csv)
            
    def test_init(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        self.assertTrue(sst.params, "params not found!")

    def test_cmd_gen(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        sst.sim_opts["mpi"] = True
        cmd = sst.assemble_command()
        self.assertIn("mpirun", cmd)

    def test_params_enum(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        self.assertEqual(len(sst.params), 4)
    
    def test_get_ext_time(self):
        test_str = "Simulation is complete, simulated time: 12.3 ms"
        t_correct = 12300
        t_get = sst_simu.SSTSimulator._get_exe_time(test_str)
        self.assertEqual(t_get, t_correct)
       
    def test_add_metri_to_header(self):
        header = ["foo", "bar"]
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        header_after = sst._add_metrics_to_header(header,
                        sst.stats)
    
    def test_compile_output(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        sst.compile_output("gist/tests/test_output")
        with open("gist/tests/test_output/summary.csv", "r") as smy, \
             open("gist/tests/test_output/summary_gold.csv", "r") as gold:
            str_1 = smy.read()
            str_2 = gold.read()
            self.assertEqual(str_1, str_2)
       
if __name__ == '__main__':
    unittest.main()

