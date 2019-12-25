#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import statistics
from string import Template
from collections import namedtuple, defaultdict
import datetime
import time
import re
import gzip
import argparse
import configparser
import logging
from functools import wraps

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

parser_args = argparse.ArgumentParser()
parser_args.add_argument('-c', '--config', default='config.ini')
parser_args.add_argument('-l', '--level', default='i')
args = parser_args.parse_args()

detail_log = True if args.level == 'i' else False

config = {
    'REPORT_SIZE': 1000,
    'report_dir': './reports1',
    'log_dir': './log1',
    'log_file': './report.log'
}

FilePath = namedtuple('FilePath', 'file_name date ext')


def log(msg_err=''):
    def dec(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                if detail_log:
                    msg = 'вызов функции {} с аргументами: {}, {} выполнен'.format(func.__name__, args, kwargs)
                    logging.info(msg + '\n' + func.__doc__)
                    logging.info(f'working time of function {func.__name__}: {time.time() - start_time} seconds')
                return result
            except:
                logging.exception(msg_err)
        return wrap
    return dec


def build_config():
    """Return aggregated dictionary from internal settings and external file

        Keyword arguments:
        config -- internal configuration parameters (dict)

        """
    if not os.path.exists(args.config):
        sys.exit('Config file is not exist. Check and try again!')

    parser = configparser.ConfigParser()

    try:
        parser.read(args.config)
    except configparser.ParsingError:
        sys.exit('Config file is incorrect. Fix and try again!')

    for k in config.keys():
        config[k.lower()] = config.pop(k)
    config.update(dict(parser.items('SETTINGS')))
    cfg = config.copy()
    return cfg


@log('Error with finding log file')
def find_log(log_dir):
    """Return named tuple with file name, log date and extention.

        Keyword arguments:
        config -- configuration parameters (dict)

        """
    pattern = '^nginx-access-ui(\.log|)-\d{8}\.(gz|log)$'
    max_date = datetime.datetime.strptime('1900-1-1 00:00:00', '%Y-%m-%d %H:%M:%S')
    file_path = None
    files = os.listdir(log_dir)

    for file in files:
        m = re.match(pattern, file)
        if m:
            # ext = 'gz' if file.endswith('.gz') else 'log'
            ext = m.group(3)
            try:
                date = datetime.datetime.strptime(m.group(2), '%Y%m%d')
                if date > max_date:
                    file_path = FilePath(file, date, ext)
                    max_date = date
            except ValueError:
                logging.exception(f'The date in the file name {file} does not match YYYYMMDD')
            except:
                logging.exception(f'Error with proccess of {file} file')
    if file_path:
        return file_path
    logging.info('No data to process')


def open_file(file_dir, mode, encoding, ext=''):
    if ext == 'gz':
        return gzip.open(file_dir, mode=mode, encoding=encoding)
    elif ext == 'zip':
        pass
    else:
        return open(file_dir, mode=mode, encoding=encoding)


@log('File parsing error')
def parser_log(file_path, log_dir, err_lines):
    """Return generator object.

        Keyword arguments:
        config -- configuration parameters (dict)
        file_path -- named tuple = the result of find_log function
        """
    file_dir = os.path.join(log_dir, file_path.file_name)
    # if os.stat(file_dir).st_size != 0:
    # f = gzip.open(file_dir, mode='rb') if file_path.ext == 'gz' else open(
    #     file_dir, encoding='utf-8')
    total_lines = err_counts = 0
    with open_file(file_dir, 'rt', 'utf-8', ext=file_path.ext) as f:
        for line in f:
            total_lines += 1
            try:
                # line = line.decode('utf-8') if file_path.ext == 'gz' else line
                # if line.find(' "0" ') != -1:
                #     continue
                line = line.split()
                url = line[6]
                time_request = float(line[len(line) - 1])
                parsed_line = [url, time_request]
                yield parsed_line
            except:
                err_counts += 1
    if total_lines and err_counts / total_lines * 100 > float(err_lines):
        logging.error(f"Allowed error rate {err_lines} exceeded")
        sys.exit('Allowed error rate exceeded. Report not generated')


@log()
def is_report_exist(file_date, report_dir):
    """Return boolean value. Check if report on required date already exists

        Keyword arguments:
        file_date -- required date
        config -- configuration parameters (dict)
        """
    return os.path.exists(os.path.join(report_dir, 'report-' + file_date.strftime("%Y.%m.%d") + '.html'))


@log('Error with preparing aggregate statistics')
def aggregate_stat(file_path, log):
    """Function aggregates statistics

        Keyword arguments:
        file_path -- named tuple = the result of find_log function
        log_dir -- log directory (str)
        """

    url_stats = defaultdict(list)
    report_url = []
    total_amount = total_time = 0

    for url, time_request in log:
        url_stats[url].append(time_request)      

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
            time_perc = round((time_sum / total_time * 100), 2)

            report_url.append({'url': k, 'count': count, 'count_perc': count_perc,
                               'time_avg': time_avg, 'time_max': time_max,
                               'time_med': time_med, 'time_perc': time_perc, 'time_sum': round(time_sum, 3)})

        report_url = sorted(report_url, key=lambda url: url['time_sum'], reverse=True)
        return report_url
    logging.info('The file is empty. Report not generated')


@log('Report generation error')
def create_report(config, file_date, report_url):
    """Function generates a report

    Keyword arguments:
    file_path -- named tuple = the result of find_log function
    config -- configuration parameters (dict)
    """

    with open('report.html', 'r') as f:
        template = f.read()

    report_content = Template(template).safe_substitute({'table_json': report_url[:config.get('report_size')]})
    report_dir = config.get('report_dir')

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    report_path = os.path.join(report_dir, 'report-' + file_date.strftime('%Y.%m.%d') + '.html')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    logging.info(f'Report is generated: {report_path}')


def main():
    cfg = build_config()
    log_levels = {'i': logging.INFO,
                  'e': logging.ERROR}


    logging.basicConfig(
        filename=cfg.get('log_file'),
        format="%(asctime)s %(levelname).1s %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
        level=log_levels.get(args.level)
    )

    file_path = find_log(cfg.get("log_dir"))
    if file_path:
        report_exist = is_report_exist(file_path.date, cfg.get('report_dir'))
    if report_exist:
        logging.info(f'Report on date {file_path.date.strftime("%Y.%m.%d")} already exists')
        sys.exit()

    if file_path:
        log = parser_log(file_path, cfg.get('log_dir'), cfg.get('err_lines'))
        report_url = aggregate_stat(file_path, log)
        if report_url:
            create_report(config, file_path.date, report_url)


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception('Program execution error')
