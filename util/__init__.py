#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common file
"""

# ---------
# Change Logs:
#
# ---------

__author__ = 'Li Pidong'
__email__ = 'lipidong@126.com'
__version__ = '0.0.3'
__status__ = 'Beta'

import os
import logging
from datetime import datetime
import subprocess


sjm_paras = {
    'memory': '1G',
    'thread': 1,
    'queue': 'all.q'
}

def safe_open(infile, mode):
    if infile.endswith('.gz'):
        import gzip
        return gzip.open(infile, mode)
    else:
        return open(infile, mode)


def get_basename(path):
    """return the path's base name without extension name

    Args:
        path (path): file path

    Returns: base name

    """
    return os.path.splitext(os.path.basename(path))[0]


def sub_basename(path, ext, mid=''):
    """substitute the extension name for the path's base name

    Args:
        path (str): path
        ext (str): extension name

    Returns: new base name

    """
    return '{name}{mid}.{ext}'.format(
        name=get_basename(path),
        mid=mid,
        ext=ext)

def read_table(_file_name, comment='#'):
    """
    :_file_name: file name
    :returns: list

    """
    with safe_open(_file_name, 'r') as f:
        for line in f:
            if comment and line.startswith(comment):
                continue
            yield line.strip().split('\t')


def read_line(path):
    """read file line by line

    Args:
        path (str): file path

    Returns: list

    """
    with open(path) as f:
        return [xx.rstrip() for xx in f.readlines()]


def mkdir(path, mode=0o777, dir_fd=None):
    """ creates a directory, even exists

    Args:
        path (str): path name

    """
    if not os.path.exists(path):
        os.mkdir(path, mode=mode, dir_fd=dir_fd)


def log(file_name, logger_name='lipidong', quite=False):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        "%(asctime)s-%(levelname)s-%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    formatter.formatTime('%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(file_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    if not quite:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger


def time2str(dt, f='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(f)


def str2time(string, f='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(string, f)


def safe_run(shell_cmd, retry=3, has_retry=0):
    has_retry += 1
    if has_retry > retry:
        print('{0} Error'.format(shell_cmd))
        return None
    print('run {0}'.format(shell_cmd))
    P = subprocess.Popen(
        shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (P_o, P_e) = P.communicate()
    if P.returncode == 0:
        return P_o
    else:
        safe_run(shell_cmd, retry=retry, has_retry=has_retry)
