#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
usage:
    set path
    set fq_list
    update paras
        para -x:ngmlr(pacbio/ont) minimap2(map-pb/map-ont)
'''

import os

from grandflow.io import readFofn
from grandflow.Pipeline import Pipeline, Task, get_config

# 读取配置文件
config = get_config('/data/grandanalysis/grandsv/config.yaml')

# 新建流程，同时设置流程的运行的路径
path = '~/test'
sv = Pipeline('sv', path)

#mkdir log
log_path = os.path.join(path,"log")
if not os.path.exists(log_path):
    os.mkdir(log_path)

# 读取文件
# 提供多个人家，sjm会并行运算
fq_list = [
    xx for xx in readFofn('/data/grandanalysis/grandflow/example/data/test.fq.list')
]

aligner_bam_output = [
    os.path.join(path,
                 os.path.basename(xx).replace('fq', 'bam')) for xx in fq_list
]

# ngmlr module
config['ngmlr'].update({
    'ref': ('/data/xieshang/database/ftp.1000genomes.ebi.ac.uk/vol1/ftp/'
            'technical/reference/human_g1k_v37.fasta'),
    'fq':
    fq_list,
    'output':
    aligner_bam_output
})

# 新建任务
# 参数分别是
# 任务名称
# 任务 cmd， 可能会包含 {}
# cmd_paras 命令行的参数
# sjm_paras sjm的参数
ngmlr = Task(
    'ngmlr',
    config['ngmlr']['cmd'],
    cmd_paras=config['ngmlr'],
    sjm_paras=config['ngmlr'])

# ngmlr 模块加入到流程中
sv.add_task(ngmlr)

# merge
merge_bam_output = os.path.join(path, 'merge.bam')
merge_bam = Task(
    'merge_bam',
    'samtools merge {output_bam} {input_bam}'.format(
        output_bam=merge_bam_output, input_bam=' '.join(aligner_bam_output)),
    sjm_paras=config['sniffles'])

# 模块的先后循序，所以需要设定前一个模块的名称
sv.add_task(merge_bam, prev_task=ngmlr)

# sniffles
sniffles_output = os.path.join(path, 'sniffles_output.vcf')
config['sniffles'].update({
    'bam': merge_bam_output,
    'output': sniffles_output
})
sniffles = Task(
    'sniffles',
    config['sniffles']['cmd'],
    cmd_paras=config['sniffles'],
    sjm_paras=config['sniffles'])

sv.add_task(sniffles, merge_bam)

# 生成sjm运行文件
sv.sjm('%s/sv.sjm.txt'%(path))
# 生成shell脚本
sv.shell('%s/sv.shell.sh'%(path))
