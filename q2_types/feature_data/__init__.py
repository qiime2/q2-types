# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat)
from ._type import (
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence)

# TODO remove these imports when tests are rewritten. Remove from __all__ too
from ._transformer import DNAIterator, PairedDNAIterator

__all__ = [
    'TaxonomyFormat', 'TaxonomyDirectoryFormat', 'DNAFASTAFormat',
    'DNASequencesDirectoryFormat', 'PairedDNASequencesDirectoryFormat',
    'AlignedDNAFASTAFormat', 'AlignedDNASequencesDirectoryFormat',
    'FeatureData', 'Taxonomy', 'Sequence', 'PairedEndSequence',
    'AlignedSequence', 'DNAIterator', 'PairedDNAIterator']

importlib.import_module('q2_types.feature_data._transformer')
