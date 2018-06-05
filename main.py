#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
create a sv pipeline
"""

# ---------
# Change Logs:
#
# ---------

__author__ = 'Li Pidong'
__email__ = 'lipidong@126.com'
__version__ = '0.0.1'
__status__ = 'Dev'

import sys
import argparse
import logging
import pdb

from grandflow.Pipeline import Pipeline, Task, get_config, aligner, sv_caller
from grandflow.util import mkdir, sub_basename, sjm_paras, read_line
from grandflow.sv import sv


def get_args():
    common_parser = argparse.ArgumentParser(prog='create a sv pipeline')
    common_parser.add_argument('--proj_name',
                        help='project name',
                        required=True)
    common_parser.add_argument('--proj_path',
                        help='project path',
                        required=True)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='SV module',
        # help='sub-command'
    )
    sv_parser = subparsers.add_parser(
                            'SV',
                            parents = [common_parser],
                            conflict_handler='resolve')
    sv_parser.add_argument('--fq_list_file',
                        help='the file path including fastq - one per line',
                        required=True)
    sv_parser.add_argument('--config',
                        help='configure file',
                        required=True)
    sv_parser.add_argument('--ref_version',
                        default='hg38',
                        choices=['hg19', 'hg38'],
                        help='the version of human genome, default=%(default)s')
    sv_parser.add_argument('--split_fq_num',
                        default=None,
                        help='the number of file to be splited if the fastq is large;'
                        'None mean no split, default=%(default)s')
    sv_parser.add_argument('--aligner',
                        default='ngmlr',
                        help='choose a aligner, default=%(default)s',
                        choices=['ngmlr', 'last', 'minimap2'])
    sv_parser.add_argument('--sv_caller',
                        default='sniffles',
                        help='choose a sv caller, default=%(default)s',
                        choices=['sniffles', 'picky', 'pbhoney'])

    if len(sys.argv)<2:
        parser.print_help();
    # else:
        # args = parser.parse_args()
    # pdb.set_trace()
    sv(parser.parse_args())
    # sv_parser.set_defaults(func=sv)


def main():
    get_args()


if __name__ == '__main__':
    main()
