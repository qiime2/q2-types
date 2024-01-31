# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import itertools
import gzip


def _read_fastq_seqs(filepath):
    # This function is adapted from @jairideout's SO post:
    # http://stackoverflow.com/a/39302117/3424666
    fh = gzip.open(filepath, 'rt')
    for seq_header, seq, qual_header, qual in itertools.zip_longest(*[fh] * 4):
        yield (seq_header.strip(), seq.strip(), qual_header.strip(),
               qual.strip())


# TODO: Remove _PlotQualView once QIIME 2 #220 completed
class _PlotQualView:
    """
    A very simple pass-through view which is made up of a single-end or
    paired-end directory format with a bool indicating if single or paired.
    """
    def __init__(self, directory_format, paired):
        self.directory_format = directory_format
        self.paired = paired
