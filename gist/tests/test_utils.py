import unittest
from .. import utils


class UtilTest(unittest.TestCase):
    def test_json_to_dict(self):
        fp = open("examples/sst_example.json", "r")
        d = utils.json_to_dict(fp)
        self.assertIsInstance(d, dict)
        fp.close()

    def test_logger_debug(self):
        logger = utils.init_logger(level="DEBUG")
        level = logger.getEffectiveLevel()
        self.assertEqual(level, 10)

    def test_get_input_basic(self):
        arg_parser = utils.add_default_arg_parser()
        args = arg_parser.parse_args(["README.md", ".gitignore"])
        in_files = utils.get_input_files_from_args(args)
        self.assertEqual(len(in_files), 2)

    def test_get_input_type(self):
        arg_parser = utils.add_default_arg_parser()
        args = arg_parser.parse_args(["README.md", ".gitignore"])
        in_files = utils.get_input_files_from_args(args, file_type=".md")
        self.assertEqual(len(in_files), 1)

    def test_get_input_from_dir(self):
        arg_parser = utils.add_default_arg_parser()
        args = arg_parser.parse_args(["--input-dir", "."])
        in_files = utils.get_input_files_from_args(args)
        self.assertEqual(len(in_files), 3)
        arg_parser = utils.add_default_arg_parser()
        args = arg_parser.parse_args(["--input-dir", "."])
        in_files = utils.get_input_files_from_args(args, file_type=".md")
        self.assertEqual(len(in_files), 1)

    def test_find_time_unit(self):
        in_str = " blah foo bar time is 1.23 ns."
        res = utils.find_time_unit(in_str)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "1.23")
        self.assertEqual(res[0][1], "ns")
        in_str_2 = "have 2 time units here 0.5ns and 1ps"
        res_2 = utils.find_time_unit(in_str_2)
        self.assertEqual(len(res_2), 2)
        self.assertEqual(res_2[0][0], "0.5")
        self.assertEqual(res_2[0][1], "ns")

        in_str_3 = "1us"
        res_3 = utils.find_time_unit(in_str_3)
        self.assertEqual(len(res_3), 1)
        self.assertEqual(res_3[0][0], "1")
        self.assertEqual(res_3[0][1], "us")

    def test_find_bw_unit(self):
        in_str = "bw is 10 GB/s and 1GB/s, not 1Gb/s"
        res = utils.find_bw_unit(in_str)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0][0], "10")
        self.assertEqual(res[0][1], "GB/s")

    def convert_time_str(self):
        in_str = "1us"
        t, u = utils.convert_time_str(in_str, "ns")
        self.assertEqual(t, 1000)
        self.assertEqual(u, "ns")

        in_str = "100ns"
        t, u = utils.convert_time_str(in_str, "us")
        self.assertEqual(t, 0.1)
        self.assertEqual(u, "us")

if __name__ == '__main__':
    unittest.main()
