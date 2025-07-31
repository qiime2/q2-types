import time
from q2_types.per_sample_sequences._formats import _PairedEndFastqManifestV2

mf_path = ('/Users/macabewood/internship/q2-types/q2_types/'
           'per_sample_sequences/tests/data/benchmarking/large_manifest')
fmt = _PairedEndFastqManifestV2(mf_path, mode='r')
start_time = time.time()

fmt.validate()

end_time = time.time()
print(end_time - start_time)
