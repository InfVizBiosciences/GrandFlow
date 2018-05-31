import pdb

from grandflow.io import VcfReader

vr = VcfReader('data/test.vcf')
for xx in vr:
    print('chrom:' + xx.chrom)
    print('id:' + xx.id)
    print(xx.info)
    pdb.set_trace()
