#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import statistics
from string import Template
from collections import namedtuple
import datetime
import time
import re
import gzip
import argparse
import configparser
import logging

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    'REPORT_SIZE': 1000,
    'report_dir': './reports1',
    'log_dir': './log1'
}


def find_log(config):
    """Return named tuple with file name, log date and extention.

        Keyword arguments:
        config -- configuration parameters (dict)

        """
    try:
        FilePath = namedtuple('FilePath', 'file_name date ext')
        pattern = '^nginx-access-ui(\.log|)-\d{8}\.(gz|log)$'
        max_date = datetime.date(1900, 1, 1)
        file_path = None
        files = os.listdir(config.get("log_dir"))

        for file in files:
            if re.match(pattern, file):
                ext = 'gz' if file.endswith('.gz') else 'log'
                date_indx = file.rfind('.')
                y = int(file[date_indx - 8: date_indx - 4])
                m = int(file[date_indx - 4: date_indx - 2])
                d = int(file[date_indx - 2: date_indx])

                date = datetime.date(y, m, d)
                if date > max_date:
                    file_path = FilePath(file, date, ext)
                    max_date = date
        if file_path:
            return file_path
        else:
            logging.info('No data to process')
    except Exception as e:
        logging.exception('file search error')


def parser_log(file_path, config):
    """Return generator object.

        Keyword arguments:
        config -- configuration parameters (dict)
        file_path -- named tuple = the result of find_log function
        """
    file_dir = os.path.join(config["log_dir"], file_path.file_name)
    if os.stat(file_dir).st_size != 0:
        try:
            f = gzip.open(file_dir, mode='rb') if file_path.ext == 'gz' else open(
                file_dir, encoding='utf-8')
            total_lines = err_lines = 0
            for line in f:
                total_lines += 1
                try:
                    line = line.decode('utf-8') if file_path.ext == 'gz' else line
                    if line.find(' "0" ') != -1:
                        continue
                    else:
                        url_start = line.find(" ", line.find('+0300]') + 8)
                        url_end = line.find(' HTTP')

                        url = line[url_start + 1: url_end]
                        time_indx = line.rfind('" ')
                        time_request = float(line[time_indx + 2:len(line)])
                        parsed_line = [url, time_request]
                        yield parsed_line

                except Exception as e:
                    err_lines += 1
            if err_lines / total_lines * 100 > float(config.get('err_lines')):
                logging.error(f"Allowed error rate {config.get('err_lines')} exceeded")
                sys.exit('Allowed error rate exceeded. Report not generated')

        except Exception as e:
            logging.exception('File parsing error')
        finally:
            f.close()
    else:
        logging.info('file is empty')


def is_report_exist(file_date, config):
    """Return boolean value. Check if report on required date already exists

        Keyword arguments:
        file_date -- required date
        config -- configuration parameters (dict)
        """
    files = os.listdir(config.get('report_dir'))

    for file in files:
        y = int(file[7: 11])
        m = int(file[12:14])
        d = int(file[15:17])
        date = datetime.date(y, m, d)
        if datetime.date(y, m, d) == file_date:
            logging.info(f'Report on date {date} already exists')
            return True
    return False


def create_report(file_path, config):
    """Function generates a report

        Keyword arguments:
        file_path -- named tuple = the result of find_log function
        config -- configuration parameters (dict)
        """
    try:
        log = parser_log(file_path, config)

        url_stats = {}
        report_url = []
        total_amount = 0
        total_time = 0

        for line in log:
            url = line[0]
            time_request = line[1]
            if url_stats.get(url):
                url_stats[url].append(time_request)
            else:
                url_stats[url] = [time_request]

            total_amount += 1
            total_time += time_request

        if total_amount:
            for k, v in url_stats.items():
                count = len(v)
                count_perc = round(count / total_amount, 3) * 100
                time_avg = round(statistics.mean(v), 3)
                time_max = max(v)
                time_med = round(statistics.median(v), 3)
                time_sum = sum(v)
                time_perc = round(time_sum / total_time, 3) * 100

                report_url.append(dict(url=k, count=count, count_perc=count_perc,
                                       time_avg=time_avg, time_max=time_max,
                                       time_med=time_med, time_perc=time_perc, time_sum=round(time_sum, 3)))

            report_url = sorted(report_url, key=lambda url: url['time_sum'])

            with open('report.html', 'r') as f:
                template = f.read()

            report_content = Template(template).safe_substitute({'table_json': report_url[:config.get('report_size')]})

            if not os.path.exists(config["report_dir"]):
                os.makedirs(config["report_dir"])

            report_path = os.path.join(config["report_dir"], 'report-' + file_path.date.strftime('%Y.%m.%d') + '.html')

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logging.info(f'Report is generated: {report_path}')
            return True
        else:
            logging.info('The file is empty. Report not generated')
            return False
    except Exception as e:
        logging.exception('Report generation error')


if __name__ == "__main__":

    # config settings
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.ini')
    args = parser.parse_args()

    if not os.path.exists(args.config):
        sys.exit('Config file is not exist. Check and try again!')

    for k in config.keys():
        config[k.lower()] = config.pop(k)

    parser = configparser.ConfigParser()

    try:
        parser.read(args.config)
    except configparser.ParsingError:
        sys.exit('Config file is incorrect. Fix and try again!')

    config.update(dict(parser.items('SETTINGS')))

    # log settings
    logging.basicConfig(
        filename=config.get('log_file'),
        format="%(asctime)s %(levelname).1s %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.INFO
    )

    # start to create report
    start_time = time.time()
    file_path = find_log(config)
    logging.debug(f'File search time: {time.time() - start_time} seconds')

    if file_path:
        if not is_report_exist(file_path.date, config):
            start_time = time.time()
            create_report(file_path, config)
            logging.debug(f'Report generation time: {time.time() - start_time} seconds')
