import unittest
import os
from collections import namedtuple
import datetime
import logging
from log_analyzer import *


class TestFindLog(unittest.TestCase):

    def test_file_log_exist(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertEqual(find_log('./log'),
                         FilePath(file_name='nginx-access-ui-20170820.log',
                                  date=datetime.datetime.strptime('20170820', '%Y%m%d'),
                                  ext='log'))

    def test_file_log_not_exist(self):
        FilePath = namedtuple('FilePath', 'file_name date ext')
        self.assertEqual(find_log('./log2'), None)

    def test_report_exist(self):
        self.assertTrue(is_report_exist(datetime.datetime.strptime('20170820', '%Y%m%d'),
                                        './reports'))

    def test_report_not_exist(self):
        self.assertFalse(is_report_exist(datetime.datetime.strptime('20170825', '%Y%m%d'),
                                         './reports'))

    def test_build_config(self):
        config = {'log_dir': './log', 'log_file': './report.log', 'report_dir': './reports',
                  'report_size': 1000, 'err_lines': '20'}
        self.assertEqual(build_config(), config)

    def test_aggregate_stat(self):
        report_url = aggregate_stat(FilePath(file_name='nginx-access-ui-20170820.log',
                                  date=datetime.datetime.strptime('20170820', '%Y%m%d'),
                                  ext='log'), './log', 20)
        self.assertTrue(len(report_url) == 256565)

    def test_create_report(self):
        config = {'log_dir': './log', 'log_file': './report.log', 'report_dir': './reports',
                  'report_size': 1000, 'err_lines': '20'}
        report_url = [{"url": "/api/v2/internal/html5/phantomjs/queue/?wait=1m", "count": 2767, "count_perc": 0.1, "time_avg": 62.995,
         "time_max": 9843.569, "time_med": 60.073, "time_perc": 9.04, "time_sum": 174306.352}]
        file_date = datetime.datetime.strptime('20170820', '%Y%m%d')
        # self.assertFalse(os.path.exists(os.path.join(config.get('report_dir'), 'report-' + file_date.strftime("%Y.%m.%d") + '.html')))
        create_report(config, file_date, report_url)
        self.assertTrue(os.path.exists(
            os.path.join(config.get('report_dir'), 'report-' + file_date.strftime("%Y.%m.%d") + '.html')))



if __name__ == "__main__":
    unittest.main()
