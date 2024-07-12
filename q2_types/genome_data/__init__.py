# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, LociDirectoryFormat,
    GFF3Format, OrthologFileFmt, SeedOrthologDirFmt,
    GenomeSequencesDirectoryFormat, OrthologAnnotationDirFmt,
)
from ._transformer import IntervalMetadataIterator
from ._type import (
    GenomeData, Genes, Proteins, Loci, Orthologs, DNASequence, NOG
)

__all__ = [
    'GenomeData', 'Genes', 'Proteins', 'Loci', 'GFF3Format',
    'GenesDirectoryFormat', 'ProteinsDirectoryFormat', 'LociDirectoryFormat',
    'IntervalMetadataIterator', 'OrthologFileFmt', 'Orthologs',
    'SeedOrthologDirFmt', 'GenomeSequencesDirectoryFormat', 'DNASequence',
    'OrthologAnnotationDirFmt', 'NOG'
    ]

importlib.import_module('q2_types.genome_data._format')
importlib.import_module('q2_types.genome_data._transformer')
importlib.import_module('q2_types.genome_data._type')
