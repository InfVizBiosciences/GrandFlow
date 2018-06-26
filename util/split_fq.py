#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
desc
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
# reload(sys)
# sys.setdefaultencoding(utf-8')
import argparse
import logging
import pdb

from grandflow.util import read_line, safe_open


def split_fq(input_list, line_num, prefix):
    """TODO: Docstring for split_fq.

    Args:
        input_list (TODO): TODO
        line_num (TODO): TODO
        prefix (TODO): TODO

    Returns: TODO

    """
    index=0
    assert line_num % 4 == 0, 'fastq must... '

    output_f_list = []
    # line_num -= 1
    chunk_num = 0
    for file_name in read_line(input_list):
        with safe_open(file_name, 'r') as f:
            for line in f:
                if index == line_num or index == 0:
                    index = 0
                    try:
                        output_f.close() # close old chunk file
                    except:
                        pass
                    output_file_name = '{prefix}.{chunk_num}.fq.gz'.format(
                        prefix=prefix,
                        chunk_num=chunk_num)
                    output_f = safe_open(output_file_name, 'w')
                    output_f_list.append(output_file_name)
                    chunk_num += 1
                output_f.write(line.encode('utf-8'))
                index += 1
        with open('{prefix}.split.fq.list'.format(prefix=prefix), 'w') as f:
            f.write('\n'.join(output_f_list))


def get_args():
    parser = argparse.ArgumentParser(prog='desc')
    parser.add_argument('--fq_list', help='输入文件列表')
    parser.add_argument('--line_num', help='小文件行数', type=int)
    parser.add_argument('--prefix', help='fq 前缀')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    return parser.parse_args()

def main():
    args = get_args()
    input_list = args.fq_list
    line_num = args.line_num
    prefix = args.prefix
    # output_list_file = args.output_list_file

    split_fq(input_list, line_num, prefix)

if __name__ == '__main__':
    main()
