# GrandFlow 说明


## 代码规范

参考 http://zh-google-styleguide.readthedocs.io/en/latest/contents/

文档涉及了C++、Python、Shell等语言


## 安装

支持python3

```
# 宝德云
export PYTHONPATH=/data/grandanalysis:$PYTHONPATH

```

## 使用

使用例子

```
cd example
```

读取 fastq

```
from grandflow.io import FastqReader

fr = FastqReader('./data/test.fq.gz')
for xx in fr:
    print('header:' + xx.header)
    print('comment:' + xx.comment)
    print('sequence:' + xx.sequence[:100])
    break
```

读取 vcf

```

from grandflow.io import VcfReader

vr = VcfReader('./data/test.vcf')
for xx in vr:
    print('chrom:' + xx.chrom)
    print('id:' + xx.id)
    print(xx.info)
    break
```


## 文档

更详细的内容，可以参考GrandFlow文档

https://grandomics-bioinfo.github.io/GrandFlow/

http://192.168.1.200:8001/index.html (北京地区IP访问)

文档采用Sphinx，根据docstring自动生成

    文档采用 Google Style Python Docstrings, 示例：http://www.sphinx-doc.org/en/stable/ext/example_google.html

## Github 使用

Github页面：https://github.com/Nextomics/GrandFlow

Github介绍：http://118.26.69.170:8000/doku.php?id=%E5%B8%8C%E6%9C%9B%E7%BB%84%E7%94%9F%E4%BF%A1%E9%83%A8:%E7%94%9F%E4%BF%A1%E9%83%A8%E8%B5%84%E6%96%99:%E7%9F%A5%E8%AF%86%E5%88%86%E4%BA%AB:git%E4%BB%8B%E7%BB%8D

该文件夹不能直接修改，每天早晨10点git pull一次

如需修改必须 git clone/pull 至自己目录，采用单独git分支完成修改、测试，确保流程正确运行后，git merge 到主分支，git push到仓库，等待第二天早晨10的自动git pull，或请管理员手动完成。

该环节对git使用要求很高，需要重点关注。

## 作业管理系统

作业管理系统采用SJM(https://github.com/StanfordBioinformatics/SJM )进行调度。

官方说明文档：https://github.com/StanfordBioinformatics/SJM/blob/master/doc/MANUAL.txt

GrandWiki文档：http://118.26.69.170:8000/doku.php?id=%E5%B8%8C%E6%9C%9B%E7%BB%84%E7%94%9F%E4%BF%A1%E9%83%A8:%E7%94%9F%E4%BF%A1%E9%83%A8%E8%B5%84%E6%96%99:%E7%9F%A5%E8%AF%86%E5%88%86%E4%BA%AB:sjm%E4%BD%9C%E4%B8%9A%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F

```
#  sjm 每次最多投100个任务，后面的会陆陆续续投递，速度较慢。为了解决这个问题，可以设置几个参数为10000
sjm --max_running 10000 --max_dispatch 10000 --max_pending 10000 M18A0771_sv.minimap2.sjm
```

