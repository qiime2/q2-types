# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
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
    ProteinFASTAFormat, AlignedProteinFASTAFormat)
from ._type import (
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence,
    Differential, ProteinSequence, AlignedProteinSequence)

# TODO remove these imports when tests are rewritten. Remove from __all__ too
from ._transformer import (
    DNAIterator, PairedDNAIterator, AlignedDNAIterator,
    ProteinIterator, AlignedProteinIterator)

__all__ = [
    'TaxonomyFormat', 'TaxonomyDirectoryFormat', 'HeaderlessTSVTaxonomyFormat',
    'HeaderlessTSVTaxonomyDirectoryFormat', 'TSVTaxonomyFormat',
    'TSVTaxonomyDirectoryFormat', 'DNAFASTAFormat', 'DifferentialFormat',
    'DNASequencesDirectoryFormat', 'PairedDNASequencesDirectoryFormat',
    'AlignedDNAFASTAFormat', 'AlignedDNASequencesDirectoryFormat',
    'FeatureData', 'Taxonomy', 'Sequence', 'PairedEndSequence',
    'AlignedSequence', 'DNAIterator', 'PairedDNAIterator', 'FASTAFormat',
    'AlignedDNAIterator', 'Differential', 'DifferentialDirectoryFormat',
    'AlignedFASTAFormatMixin', 'ProteinFASTAFormat', 'ProteinSequence',
    'AlignedProteinFASTAFormat', 'ProteinSequencesDirectoryFormat',
    'AlignedProteinSequence', 'AlignedProteinSequencesDirectoryFormat',
    'ProteinIterator', 'AlignedProteinIterator']

importlib.import_module('q2_types.feature_data._transformer')
