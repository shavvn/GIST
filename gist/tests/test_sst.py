import unittest
from .. import sst_simu


class SSTTest(unittest.TestCase):
    def test_init(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        self.assertTrue(sst.configs, "Config not found!")

    def test_cmd_gen(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        sst.configs["sim_opts"]["mpi"] = True
        cmd = sst.assemble_command()
        self.assertIn("mpirun", cmd)

    def test_params_enum(self):
        sst = sst_simu.SSTSimulator("examples/sst_example.json")
        param_list = sst.get_all_params()
        self.assertEqual(len(param_list), 4)

if __name__ == '__main__':
    unittest.main()
