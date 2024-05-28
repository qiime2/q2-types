# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    GenesDirectoryFormat, ProteinsDirectoryFormat,
    GFF3Format, LociDirectoryFormat, OrthologFileFmt, SeedOrthologDirFmt,
)
from ._methods import collate_orthologs, partition_orthologs
from ._transformer import IntervalMetadataIterator
from ._type import (
    GenomeData, Genes, Proteins, Loci, Ortholog, BLAST6
)

__all__ = [
    'GenomeData', 'Genes', 'Proteins', 'Loci', 'GFF3Format',
    'GenesDirectoryFormat', 'ProteinsDirectoryFormat', 'LociDirectoryFormat',
    'IntervalMetadataIterator', 'OrthologFileFmt', 'Ortholog',
    'SeedOrthologDirFmt', 'BLAST6', 'collate_orthologs', 'partition_orthologs',
    ]

importlib.import_module('q2_types.genome_data._format')
importlib.import_module('q2_types.genome_data._transformer')
importlib.import_module('q2_types.genome_data._type')
