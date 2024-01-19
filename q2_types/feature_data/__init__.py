# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    TaxonomyFormat, TaxonomyDirectoryFormat, HeaderlessTSVTaxonomyFormat,
    HeaderlessTSVTaxonomyDirectoryFormat, TSVTaxonomyFormat,
    TSVTaxonomyDirectoryFormat, DNAFASTAFormat, DNASequencesDirectoryFormat,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat,
    AlignedDNASequencesDirectoryFormat, DifferentialFormat,
    DifferentialDirectoryFormat, FASTAFormat, AlignedFASTAFormatMixin,
    AlignedProteinSequencesDirectoryFormat, ProteinSequencesDirectoryFormat,
    ProteinFASTAFormat, AlignedProteinFASTAFormat, RNASequencesDirectoryFormat,
    RNAFASTAFormat, AlignedRNAFASTAFormat, AlignedRNASequencesDirectoryFormat,
    PairedRNASequencesDirectoryFormat, BLAST6Format, BLAST6DirectoryFormat,
    MixedCaseDNAFASTAFormat, MixedCaseDNASequencesDirectoryFormat,
    MixedCaseRNAFASTAFormat, MixedCaseRNASequencesDirectoryFormat,
    MixedCaseAlignedDNAFASTAFormat,
    MixedCaseAlignedDNASequencesDirectoryFormat,
    MixedCaseAlignedRNAFASTAFormat,
    MixedCaseAlignedRNASequencesDirectoryFormat)
from ._type import (
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence,
    Differential, ProteinSequence, AlignedProteinSequence, RNASequence,
    AlignedRNASequence, PairedEndRNASequence, BLAST6)

# TODO remove these imports when tests are rewritten. Remove from __all__ too
from ._transformer import (
    NucleicAcidIterator, DNAIterator, PairedDNAIterator, AlignedDNAIterator,
    ProteinIterator, AlignedProteinIterator, RNAIterator, AlignedRNAIterator,
    PairedRNAIterator, BarcodePairedSequenceFastqIterator,
    BarcodeSequenceFastqIterator)

__all__ = [
    'TaxonomyFormat', 'TaxonomyDirectoryFormat', 'HeaderlessTSVTaxonomyFormat',
    'HeaderlessTSVTaxonomyDirectoryFormat', 'TSVTaxonomyFormat',
    'TSVTaxonomyDirectoryFormat', 'DNAFASTAFormat', 'DifferentialFormat',
    'DNASequencesDirectoryFormat', 'PairedDNASequencesDirectoryFormat',
    'AlignedDNAFASTAFormat', 'AlignedDNASequencesDirectoryFormat',
    'FeatureData', 'Taxonomy', 'Sequence', 'PairedEndSequence',
    'AlignedSequence', 'NucleicAcidIterator', 'DNAIterator',
    'PairedDNAIterator', 'FASTAFormat', 'AlignedDNAIterator', 'Differential',
    'DifferentialDirectoryFormat', 'AlignedFASTAFormatMixin',
    'ProteinFASTAFormat', 'ProteinSequence', 'AlignedProteinFASTAFormat',
    'ProteinSequencesDirectoryFormat', 'AlignedProteinSequence',
    'AlignedProteinSequencesDirectoryFormat', 'ProteinIterator',
    'AlignedProteinIterator', 'RNAIterator', 'AlignedRNAIterator',
    'RNAFASTAFormat', 'AlignedRNAFASTAFormat', 'RNASequencesDirectoryFormat',
    'AlignedRNASequencesDirectoryFormat', 'RNASequence', 'AlignedRNASequence',
    'PairedRNAIterator', 'PairedRNASequencesDirectoryFormat',
    'PairedEndRNASequence', 'BLAST6Format', 'BLAST6DirectoryFormat', 'BLAST6',
    'MixedCaseDNAFASTAFormat', 'MixedCaseDNASequencesDirectoryFormat',
    'MixedCaseRNAFASTAFormat', 'MixedCaseRNASequencesDirectoryFormat',
    'MixedCaseAlignedDNAFASTAFormat',
    'MixedCaseAlignedDNASequencesDirectoryFormat',
    'MixedCaseAlignedRNAFASTAFormat',
    'MixedCaseAlignedRNASequencesDirectoryFormat',
    'BarcodePairedSequenceFastqIterator',
    'BarcodeSequenceFastqIterator']

importlib.import_module('q2_types.feature_data._transformer')
