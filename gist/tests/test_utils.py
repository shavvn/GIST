import unittest
from .. import utils


class UtilTest(unittest.TestCase):
    def test_json_to_dict(self):
        fp = open("examples/sst_example.json", "r")
        d = utils.json_to_dict(fp)
        self.assertIsInstance(d, dict)

    def test_logger_debug(self):
        arg_parser = utils.ArgParser(["-d"])
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 10)
        self.assertEqual(arg_parser.is_debug(), True)

    def test_logger_verbose(self):
        arg_parser = utils.ArgParser(["-v"])
        self.assertEqual(arg_parser.is_verbose(), True)
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 20)

    def test_logger_info(self):
        arg_parser = utils.ArgParser([""])
        self.assertEqual(arg_parser.is_verbose(), False)
        self.assertEqual(arg_parser.is_debug(), False)
        level = arg_parser.logger.getEffectiveLevel()
        self.assertEqual(level, 30)

    def test_get_input_basic(self):
        arg_parser = utils.ArgParser(["README.md", ".gitignore"])
        in_files = arg_parser.get_input_files()
        self.assertEqual(len(in_files), 2)

    def test_get_input_type(self):
        arg_parser = utils.ArgParser(["README.md", ".gitignore"])
        in_files = arg_parser.get_input_files(file_type=".md")
        self.assertEqual(len(in_files), 1)

    def test_get_input_from_dir(self):
        arg_parser = utils.ArgParser(["--input-dir", "."])
        in_files = arg_parser.get_input_files()
        self.assertEqual(len(in_files), 3)
        arg_parser = utils.ArgParser(["--input-dir", "."])
        in_files = arg_parser.get_input_files(file_type=".md")
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

    def test_find_bw_unit(self):
        in_str = "bw is 10 GB/s and 1GB/s, not 1Gb/s"
        res = utils.find_bw_unit(in_str)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0][0], "10")
        self.assertEqual(res[0][1], "GB/s")

if __name__ == '__main__':
    unittest.main()
