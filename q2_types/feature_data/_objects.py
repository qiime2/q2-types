# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections


class NucleicAcidIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


class DNAIterator(NucleicAcidIterator):
    pass


class PairedDNAIterator(NucleicAcidIterator):
    pass


class AlignedDNAIterator(NucleicAcidIterator):
    pass


class RNAIterator(NucleicAcidIterator):
    pass


class PairedRNAIterator(NucleicAcidIterator):
    pass


class AlignedRNAIterator(NucleicAcidIterator):
    pass


class ProteinIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


class AlignedProteinIterator(ProteinIterator):
    pass
