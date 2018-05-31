
from grandflow.io import FastqReader
import pdb

fr = FastqReader('data/test.fq.gz')
for xx in fr:
    print('header:' + xx.header)
    print('comment:' + xx.comment)
    print('sequence:' + xx.sequence[:100])
    pdb.set_trace()
