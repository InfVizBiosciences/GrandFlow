#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
usage:
    python3 run_aligner_picky.py ngmlr /data/suyanan/scripts/suyanan/GrandFlow/example/demo/ngmlr_picky HX1 /data/suyanan/scripts/suyanan/GrandFlow/example/demo/sample.list
    sjm --max_running 10000 --max_dispatch 10000 --max_pending 10000 sv.sjm.txt
    sjm --max_running 10000 --max_dispatch 10000 --max_pending 10000 sv.sjm.txt.status
'''

import os,sys
#import argparse

from grandflow.io import readFofn
from grandflow.Pipeline import Pipeline, Task, get_config


##------------------用户自定义参数----------------------
aligner = sys.argv[1] # "ngmlr"
path = sys.argv[2] #'/data/suyanan/scripts/suyanan/GrandFlow/example/demo/ngmlr_picky'
proj_name = sys.argv[3] # "HX1"
sample_list = sys.argv[4] #"sample.list"
#sample_suffix = 'fq.gz'  #fq/fq.gz
sample_suffix = 'fq'


# 读取配置文件
config = get_config('/data/suyanan/scripts/suyanan/GrandFlow/config/config.yaml')

# 新建流程，同时设置流程的运行的路径
sv = Pipeline('sv', path)

fq_list = [xx for xx in readFofn('%s/%s'%(path,sample_list))]

def creater_dir(dirname):
    dirpath = os.path.join(path,dirname)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    return dirpath

# alinger目录
aligner_output_path = creater_dir("1.aligner")
aligner_bam_list = [
    os.path.join(aligner_output_path,
                 os.path.basename(xx).replace(sample_suffix, 'bam')) for xx in fq_list
]

aligner_prefix_list = [
    os.path.join(aligner_output_path,os.path.basename(xx).replace('.'+sample_suffix, '')) for xx in fq_list
]
aligner_align_list = [
    os.path.join(aligner_output_path,os.path.basename(xx).replace(sample_suffix, 'align')) for xx in fq_list
]  #path/aligner_output/xxx.align

#callsv目录下
callsv_path = creater_dir("2.callsv")    
callsv_prefix_list = [
    os.path.join(callsv_path,os.path.basename(xx).replace('.'+sample_suffix, '')) for xx in fq_list
]  #path/callsv/xxx (include：xxx.profile.DEL.xls、xxx.profile.DEL.vcf , etc)

#log目录
log_path = creater_dir("log")

log_prefix_list = [
    os.path.join(log_path,os.path.basename(xx).replace('.'+sample_suffix, '')) for xx in fq_list
]  #path/log/xxx

# last_picky
config['last_picky'].update({    
    'fq':
    fq_list,    
    'align':
    aligner_align_list,
    'oprefix':
    callsv_prefix_list,
    'log_prefix':
    log_prefix_list
})
last_picky = Task(
    'last_picky',
    config['last_picky']['cmd'],
    cmd_paras=config['last_picky'],
    sjm_paras=config['last_picky'])    

# ngmlr_picky
config['ngmlr_picky'].update({    
    'fq':
    fq_list,    
    'aligner_prefix':
    aligner_prefix_list,
    'oprefix':
    callsv_prefix_list,    
})
ngmlr_picky = Task(
    'ngmlr_picky',
    config['ngmlr_picky']['cmd'],
    cmd_paras=config['ngmlr_picky'],
    sjm_paras=config['ngmlr_picky'])    

# minimap2_picky
config['minimap2_picky'].update({    
    'fq':
    fq_list,    
    'aligner_prefix':
    aligner_prefix_list,
    'oprefix':
    callsv_prefix_list,    
})
minimap2_picky = Task(
    'minimap2_picky',
    config['minimap2_picky']['cmd'],
    cmd_paras=config['minimap2_picky'],
    sjm_paras=config['minimap2_picky']) 


# picky_vcf_by_xls：对所有fq来讲，每个SV合并后转成vcf
#final目录下
picky_final_path = creater_dir("3.final") 
total_sample_prefix = os.path.join(picky_final_path,proj_name)  #path/final/XX
  
picky_svtype_list = ["DEL","INS","INDEL","INV","TTLC","TDSR","TDC"]
picky_svtype_xls_list = []
for i in range(len(picky_svtype_list)):
    each_sv_xls_files_list = []
    for j in range(len(callsv_prefix_list)):
        each_sv_xls_files = callsv_prefix_list[j]+".profile.%s.xls"%(picky_svtype_list[i])
        each_sv_xls_files_list.append(each_sv_xls_files)
    each_sv_xls_files_str = ' '.join(each_sv_xls_files_list)
    picky_svtype_xls_list.append(each_sv_xls_files_str)

# picky_vcf_by_xls
config['picky_vcf_by_xls'].update({    
    'SAMPLE':
    total_sample_prefix,
    'SVTYPE': 
    picky_svtype_list,
    'svtype_xls_files':
    picky_svtype_xls_list
})
picky_vcf_by_xls = Task(
    'picky_vcf_by_xls',
    config['picky_vcf_by_xls']['cmd'],
    cmd_paras=config['picky_vcf_by_xls'],
    sjm_paras=config['picky_vcf_by_xls'])     

# picky_vcf_by_xls_all（xls2vcf时默认--re=2两条reads支持）
config['picky_vcf_by_xls_all'].update({    
    'SAMPLE':
    total_sample_prefix,    
})
picky_vcf_by_xls_all = Task(
    'picky_vcf_by_xls_all',
    config['picky_vcf_by_xls_all']['cmd'],
    cmd_paras=config['picky_vcf_by_xls_all'],
    sjm_paras=config['picky_vcf_by_xls_all'])     

# picky_vcf_by_align
config['picky_vcf_by_align'].update({    
    'SAMPLE':
    total_sample_prefix,
    'align_files':
    ' '.join(aligner_align_list)    
})

picky_vcf_by_align = Task(
    'picky_vcf_by_align',
    config['picky_vcf_by_align']['cmd'],
    cmd_paras=config['picky_vcf_by_align'],
    sjm_paras=config['picky_vcf_by_align']) 


# 加入任务
alinger_task = ''
if aligner == 'last':
    sv.add_task(last_picky)
    alinger_task = last_picky
if aligner == 'ngmlr':
    sv.add_task(ngmlr_picky)
    alinger_task = ngmlr_picky
if aligner == 'minimap2':
    sv.add_task(minimap2_picky)
    alinger_task = minimap2_picky

sv.add_task(picky_vcf_by_xls,prev_task=alinger_task)
sv.add_task(picky_vcf_by_xls_all,prev_task=picky_vcf_by_xls)
sv.add_task(picky_vcf_by_align,prev_task=alinger_task)


#----------------------sv.py----------------------
####==========STEP1. ALIGNER=============
#ngmlr
config['ngmlr'].update({   
    'fq':
    fq_list,
    'output':
    aligner_bam_list
})
ngmlr = Task(
    'ngmlr',
    config['ngmlr']['cmd'],
    cmd_paras=config['ngmlr'],
    sjm_paras=config['ngmlr'])
    
#last
config['last'].update({    
    'fq':
    fq_list,
    'output':
    aligner_bam_list
})
last = Task(
    'last',
    config['last']['cmd'],
    cmd_paras=config['last'],
    sjm_paras=config['last'])
      
#minimap2
config['minimap2'].update({   
    'fq':
    fq_list,
    'output':
    aligner_bam_list
})
minimap2 = Task(
    'minimap2',
    config['minimap2']['cmd'],
    cmd_paras=config['minimap2'],
    sjm_paras=config['minimap2'])
   
# 加入任务aligner(ngmlr/last/minimap2)
#sv.add_task(last)


####==========STEP2. merge===========
merge_bam_output = os.path.join(path, 'aligner_merge.bam')
merge_bam = Task(
    'merge_bam',
    'samtools merge {output_bam} {input_bam}'.format(
        output_bam=merge_bam_output, input_bam=' '.join(aligner_bam_list)),
    sjm_paras=config['sniffles'])

# 加入任务
#sv.add_task(merge_bam, prev_task=last)


####==========STEP3. SVcaller=============
svcaller_output = os.path.join(path, 'svcallset.vcf')

# sniffles
config['sniffles'].update({
    'bam': merge_bam_output,
    'output': svcaller_output
})
sniffles = Task(
    'sniffles',
    config['sniffles']['cmd'],
    cmd_paras=config['sniffles'],
    sjm_paras=config['sniffles'])
    
# nanosv
#GRCH38: set [depth_support = False] in config.ini, remove paras:-b {nanosv_path}/bedfiles/human_hg19.bed
config['nanosv'].update({
    'bam': merge_bam_output,
    'output': svcaller_output
})
nanosv = Task(
    'nanosv',
    config['nanosv']['cmd'],
    cmd_paras=config['nanosv'],
    sjm_paras=config['nanosv'])
    

# 加入callsv任务(nanosv/sniffles)    
#sv.add_task(nanosv_python, merge_bam)


    
# 生成sjm运行文件
sv.sjm('%s/sv.sjm.txt'%(path))
# 生成shell脚本
sv.shell('%s/sv.shell.sh'%(path))
