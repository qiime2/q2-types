# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_types.reference_db._type import (
    ReferenceDB, Diamond, Eggnog, NCBITaxonomy,
    EggnogProteinSequences, HMMER
)

from q2_types.reference_db._format import (
    EggnogRefDirFmt,
    EggnogRefTextFileFmt,
    EggnogRefBinFileFmt,
    DiamondDatabaseFileFmt,
    DiamondDatabaseDirFmt,
    NCBITaxonomyDirFmt,
    EggnogProteinSequencesDirFmt,
    HmmerDirFmt
    )

__all__ = [
    'ReferenceDB', 'Diamond', 'Eggnog', 'DiamondDatabaseFileFmt',
    'DiamondDatabaseDirFmt', 'EggnogRefDirFmt', 'EggnogRefTextFileFmt',
    'EggnogRefBinFileFmt', 'NCBITaxonomyDirFmt', 'NCBITaxonomy',
    'EggnogProteinSequencesDirFmt', 'EggnogProteinSequences', 'HMMER',
    'HmmerDirFmt'
]

importlib.import_module('q2_types.reference_db._format')
importlib.import_module('q2_types.reference_db._type')
