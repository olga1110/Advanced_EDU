import unittest
from collections import namedtuple
import datetime
import logging
from log_analyzer import find_log, is_report_exist, create_report


class TestFindLog(unittest.TestCase):

    def test_exist_file_log(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertEqual(find_log({'log_dir': './log'}),
                         FilePath(file_name='nginx-access-ui-20170815.log', date=datetime.date(2017, 8, 15), ext='log'))

    # log2 = empty directory
    # @mock.patch(logging)
    # def test_empty_file_log(self, mock_logger):
    #     find_log({'log_dir': './log2'})
    #     mock_logger.warn.assert_called_with('No data to process')

    def test_exist_file_log(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertEqual(find_log({'log_dir': './log2'}), None)


    def test_report_exist(self):
        self.assertTrue(is_report_exist(datetime.date(2017, 8, 15), {'report_dir': './reports'}))


    def test_report_not_exist(self):
        self.assertFalse(is_report_exist(datetime.date(2017, 8, 16), {'report_dir': './reports'}))

    def create_report_correct(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertTrue(create_report(FilePath(file_name='nginx-access-ui-20170815.log',
                                               date=datetime.date(2017, 8, 15), ext='log'),
                                      {'report_dir': './reports'}))

    def create_report_incorrect(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertFalse(create_report(FilePath(file_name='nginx-access-ui-20170815.log',
                                               date=datetime.date(2017, 8, 20), ext='log'),
                                      {'report_dir': './reports'}))


if __name__ == "__main__":
    unittest.main()