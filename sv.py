#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
the module of sv
"""

# ---------
# Change Logs:
#
# ---------

__author__ = 'Li Pidong'
__email__ = 'lipidong@126.com'
__version__ = '0.0.1'
__status__ = 'Dev'

import argparse
import logging
import pdb
import sys
import os

from grandflow.Pipeline import Pipeline, Task, aligner, get_config, sv_caller
from grandflow.util import mkdir, read_line, sjm_paras, sub_basename


def sv(args):
    """the module of sv

    Args:
        args (dict): the parsers

    Returns: create sjm file

    """
    config = get_config(args.config)
    fq_list = read_line(args.fq_list_file)
    sv = Pipeline(path=args.proj_path)
    aligner_task, merge_bam_task = aligner(
        args.aligner, args.proj_name, fq_list, config, args.ref_version)
    sv.add_task(aligner_task)
    sv.add_task(merge_bam_task, prev_task=aligner_task)

    sv_caller_input_bam = merge_bam_task.output
    sv_caller_task = sv_caller(args.sv_caller, args.proj_name,
                               sv_caller_input_bam, config)
    sv.add_task(sv_caller_task, prev_task=merge_bam_task)
    sv.sjm(os.path.join(args.proj_path, '%s_sv.sjm' % args.proj_name))


def main():
    args = get_args()
    input_file = args.input_file
    log_file = args.log
    quite = args.quite
    global logger
    logger = log(log_file, quite=quite)


if __name__ == '__main__':
    main()

