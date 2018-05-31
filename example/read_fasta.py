
from grandflow.io import FastaReader
import pdb

fr = FastaReader('data/test.fasta')
for xx in fr:
    print('header:' + xx.header)
    print('sequence:' + xx.sequence[:100])
    pdb.set_trace()
