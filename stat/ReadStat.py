#!/usr/bin/env python
"""
To statistics on a list of fasta/fastq files

"""
import argparse
import collections
from multiprocessing import Pool

import numpy as np

from grandflow.io import FastaReader, FastqReader
from grandflow.plot.lib import length_plots
from grandflow.util import *

class ReadStat(object):
    """Statistic the reads length, GC content """

    def __init__(self, fqs, min_len=0, thread=1):
        """TODO: Docstring for __init__.

        Args:
            _proj_name (TODO): project name
            _fqs (list): fastq files list
            _min_len (int): count the reads which length above min_len,
                            default=0
            _thread (int): thread, default=1
        Returns: TODO

        """
        # self._proj_name = proj_name
        self._fqs = fqs
        # self._fofn = fofn
        self._min_len = min_len
        self._thread = thread

        self.total_length = None
        self.lenths = None
        self.file_list = None

    def get_length(self, filename, index, min_len):
        """
        get the length of record
        :param filename:
        :return:
        """
        r = []

        print("[%s] process %r" % (index, filename))

        fmt = filename.split(".")[-1]
        if filename.endswith(".gz"):
            fmt = ".".join(filename.split(".")[-2:])

        if fmt.lower() in ["fastq", "fq", "fastq.gz", "fq.gz"]:
            for record in FastqReader(filename):

                if record.length >= min_len:
                    r.append(record.length)

        elif fmt.lower() in ["fasta", "fa", "fasta.gz", "fa.gz"]:
            for record in FastaReader(filename):

                if record.length >= min_len:
                    r.append(record.length)
        else:
            print("[%s] %r is not a valid seq format!" % (index, filename))
        return r

    def get_fq_reads_num(self, filename):
        """
        get the number of read line
        :param filename:
        :return:
        """
        fmt = filename.split(".")[-1]
        if filename.endswith(".gz"):
            fmt = ".".join(filename.split(".")[-2:])

        if fmt.lower() in ["fastq", "fq", "fastq.gz", "fq.gz"]:
            num = 0
            for xx in safe_open(filename):
                num += 1
            return int(num/4)

        elif fmt.lower() in ["fasta", "fa", "fasta.gz", "fa.gz"]:
            num = 0
            for xx in safe_open(filename):
                num += 1
            return int(num/2)

        else:
            print("[%s] %r is not a valid seq format!" % (index, filename))


    def N(self, number, lengths):
        """
        calculate the N{number}return N{number} information of lengths
        :param number: 0-100
        :param lengths: a list of length
        :return:
        """
        assert lengths

        sum_length = sum(lengths)
        accu_len = 0
        accu_num = 0

        for i in sorted(lengths, reverse=True):
            accu_len += i
            accu_num += 1

            if accu_len >= sum_length * number / 100:
                return i, accu_num, accu_len

        return i, accu_num, accu_len

    def over(self, number, lengths):
        """
        return length in lengths over {number}
        :param number:
        :param lengths:
        :return:
        """
        assert lengths
        accu_len = 0
        accu_num = 0

        for i in sorted(lengths, reverse=True):
            if i < number:
                return i, accu_num, accu_len

            accu_len += i
            accu_num += 1

        return i, accu_num, accu_len

    def get_reads_num(self):
        """get the reads num

        Returns: the number of reads

        """
        file_list = []
        with open(self._fqs) as f:
            for xx in f:
                file_list.append(xx[:-1])
        self.file_list = file_list
        pool = Pool(processes=self._thread)
        results = []

        for i in range(len(file_list)):
            filename = file_list[i]
            results.append(
                pool.apply_async(self.get_fq_reads_num,
                                 (filename,)))
        pool.close()
        pool.join()

        reads_num = 0
        for i, r in enumerate(results):
            reads_num += r.get()
        return reads_num


    def get_length_list(self):
        """TODO: Docstring for get_total_length.

        Args:
            arg1 (TODO): TODO

        Returns: TODO

        """
        file_list = []
        with open(self._fqs) as f:
            for xx in f:
                file_list.append(xx[:-1])
        self.file_list = file_list
        pool = Pool(processes=self._thread)
        results = []

        for i in range(len(file_list)):
            filename = file_list[i]
            index = "%s/%s" % (i + 1, len(file_list))
            results.append(
                pool.apply_async(self.get_length,
                                 (filename, index, self._min_len)))
        pool.close()
        pool.join()

        lengths = []
        for i, r in enumerate(results):
            print("[%s/%s] getting results of %r" % (i + 1, len(results),
                                                     file_list[i]))
            lengths += r.get()
        self.lengths = lengths
        return lengths

    def length_stat(self):
        """
        statistics on fastq files
        :return:
            reads_stat_dict={
                'file_num': file_num,
                'reads_num': reads_number,
                'total_length': total_length,
                'average_length': average_length,
                'longest_length': longest
            }


        """

        reads_stat_dict = collections.OrderedDict()
        reads_dis_dict = collections.OrderedDict()
        # 1. get the lengths of each fastA/Q file
        # write lengths out
        lengths = sorted(self.get_length_list(), reverse=True)

        # 2. get the common statistics
        total_length = sum(lengths)
        self.total_length = total_length
        reads_number = len(lengths)
        file_num = len(self.file_list)
        average_length = int(total_length / reads_number)
        longest = lengths[0]
        # reads_number = reads_number
        # self._lengths = lengths
        reads_stat_dict = {
            'length_sort': lengths,
            'file_num': file_num,
            'reads_number': reads_number,
            'total_length': total_length,
            'average_length': average_length,
            'longest': longest
        }
        return reads_stat_dict

    def length_distribute(self):
        # 2. get the N10-N90 statstics
        # length: the N{i} value; number: number of reads which length >= N{i}
        # if the input file is ngs short reads, skip the following steps.

        length_dist_N_dict = {}
        length_dist_over_dict = {}
        total_lenth = self.total_length
        lengths = self.lengths
        for i in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
            read_length, read_number, read_length_sum = self.N(i, lengths)
            # reads_dis_dict["N%s" % i] =
            length_dist_N_dict[i] = [
                read_length, read_number,
                100.0 * read_length_sum / self.total_length
            ]

            # print("%5s\t%15s\t%15s\t%10.2f" %
            # ("N%s" % i, "{0:,}".format(read_length),
            # "{0:,}".format(read_number),
            # 100.0 * read_length_sum / total_length))

        # length: the sum of record length which length >= i; number: the number of record which length >= i
        for i in [
                1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 500, 1000
        ]:
            _, read_number, read_length_sum = self.over(i * 1000, lengths)
            length_dist_over_dict[i] = [
                read_number, read_length_sum,
                100.0 * read_length_sum / self.total_length
            ]
            # print("%5s\t%15s\t%15s\t%10.2f" %
            # (">%skb" % i, "{0:,}".format(read_length_sum),
            # "{0:,}".format(read_number),
            # 100.0 * read_length_sum / total_length))

    # write out record length for plot
    # with open("record.len", "w") as fh:
    # fh.write("\n".join(map(str, lengths)))

        return length_dist_N_dict, length_dist_over_dict

    def write_reads_stat(self, proj_name, output_path, reads_stat_dict,
                         length_dist_N_dict, length_dist_over_dict):
        """TODO: Docstring for get_.

        Args:
            arg1 (TODO): TODO

        Returns: TODO

        """

        # stdout
        reads_stat_dict_str = """
#Statistics for all FastA/Q records
file number\t{file_num:,}
record number\t{reads_number:,}
sum of length\t{total_length:,}
average length\t{average_length:,}
longest length\t{longest:,}
        """.format(**reads_stat_dict)

        with open(os.path.join(output_path,
                               '%s.reads.stat.xls' % proj_name), 'w') as f:
            f.write(reads_stat_dict_str)

        with open(
                os.path.join(output_path,
                             '%s.reads.distribute.xls' % proj_name), 'w') as f:
            f.write('#Distribution of record length\n')
            f.write('Type\tBases\tCount\t%Bases\n')
            for ii, [read_length, read_number,
                     ratio] in length_dist_N_dict.items():

                f.write(
                    "N{N}\t{read_length:,}\t{read_number:,}\t{ratio:.2f}\n".
                    format(
                        N=ii,
                        read_length=read_length,
                        read_number=read_number,
                        ratio=ratio))

            for jj, [read_number, read_length_sum,
                     ratio] in length_dist_over_dict.items():
                f.write('>{N}kb\t{read_length_sum:,}\t{read_number:,}\t{raito:.2f}\n'.
                        format(
                            N=jj,
                            read_length_sum=read_length_sum,
                            read_number=read_number,
                            raito=ratio))
        N50 = length_dist_N_dict[50][0]
        length_plots(
            np.array(self.lengths),
            'length',
            os.path.join(output_path, proj_name + '.'),
            n50=N50,
            title=proj_name)


def get_args():
    """
    get args
    :return:
    """
    args = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
description:
    Statistics on FastA/Q files
    file number
    record number
    sum of length
    average length
    longest length
    N50-N90
         """)

    args.add_argument("--fq_list", help="file including fastq  paths")
    args.add_argument("--proj_name", help="project name ")
    args.add_argument("--output_dir", help="output directory ")
    args.add_argument(
        "--min_len",
        type=int,
        metavar="INT",
        default=0,
        help="min length to statistics")
    args.add_argument(
        "-t",
        "--thread",
        metavar='INT',
        type=int,
        default=1,
        help="number of thread process")

    return args.parse_args()


def main():
    args = get_args()
    rs = ReadStat(args.fq_list,args.min_len, args.thread)
    reads_stat_dict = rs.length_stat()
    length_dist_N_dict, length_dist_over_dict = rs.length_distribute()
    rs.write_reads_stat(args.proj_name, args.output_dir, reads_stat_dict,
                        length_dist_N_dict, length_dist_over_dict)


if __name__ == "__main__":
    main()
