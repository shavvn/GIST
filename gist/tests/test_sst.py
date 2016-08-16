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

    def test_ember_output_line(self):
        line_1 = "Ring total time 1308.114 us, loop 1, bufLen 1, " \
                 "latency 1.236 us. bandwidth 0.000809 GB/s"
        results = sst_simu.get_ember_output_from_line(line_1)
        tgt_dict = {
            "real_latency(us)": "1.236",
            "real_bandwidth(GB/s)": "0.000809",
            "work_time(us)": "1308.114"
        }
        self.assertEqual(tgt_dict, results)

if __name__ == '__main__':
    unittest.main()

