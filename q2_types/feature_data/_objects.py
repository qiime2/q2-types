# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections

from skbio.sequence import DNA, GrammaredSequence, NucleotideMixin
from skbio.util import classproperty


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


class LinkedDNA(GrammaredSequence, NucleotideMixin):
    '''
    This type provides the subset of functionality of `skbio.DNA` that makes
    sense for linked sequences.
    '''
    @classproperty
    def definite_chars(cls):
        return DNA.definite_chars

    @classproperty
    def degenerate_map(cls):
        return DNA.degenerate_map

    @classproperty
    def gap_chars(cls):
        return DNA.gap_chars | set(' ')

    @classproperty
    def default_gap_char(cls):
        return DNA.default_gap_char

    @classproperty
    def wildcard_char(cls):
        return DNA.wildcard_char

    @classproperty
    def complement_map(cls):
        return {**DNA.complement_map, ' ': ' '}

    def gaps(self):
        raise TypeError(
            'Different gap characters have different semantics in `LinkedDNA`.'
        )

    def has_gaps(self):
        raise TypeError(
            'Different gap characters have different semantics in `LinkedDNA`.'
        )

    def degap(self):
        raise TypeError(
            'Different gap characters have different semantics in `LinkedDNA`.'
        )
