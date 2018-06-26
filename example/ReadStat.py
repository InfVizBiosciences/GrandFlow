#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
the example of stat/ReadStat class
"""

# ---------
# Change Logs:
#
# ---------
from grandflow.stat.ReadStat import ReadStat

rs = ReadStat.ReadStat('data/test.fq.list',thread=4)
reads_num = rs.get_reads_num() # get the number of reads
reads_stat_dict = rs.length_stat()
length_dist_N_dict, length_dist_over_dict = rs.length_distribute()
rs.write_reads_stat('read_stat', # project name
                    '~/test/', # output path
                    reads_stat_dict,
                    length_dist_N_dict,
                    length_dist_over_dict)
