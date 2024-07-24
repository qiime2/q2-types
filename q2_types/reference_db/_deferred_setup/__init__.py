# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .. import (
    ReferenceDB, Diamond, Eggnog, NCBITaxonomy,
    EggnogProteinSequences,
    EggnogRefDirFmt,
    EggnogRefTextFileFmt,
    EggnogRefBinFileFmt,
    DiamondDatabaseFileFmt,
    DiamondDatabaseDirFmt,
    NCBITaxonomyDirFmt,
    NCBITaxonomyBinaryFileFmt,
    NCBITaxonomyNamesFormat,
    NCBITaxonomyNodesFormat,
    EggnogProteinSequencesDirFmt
)

from ...plugin_setup import plugin


plugin.register_semantic_types(
    ReferenceDB, Diamond, Eggnog, NCBITaxonomy, EggnogProteinSequences
)

plugin.register_formats(
    EggnogRefTextFileFmt, EggnogRefBinFileFmt, EggnogRefDirFmt,
    DiamondDatabaseFileFmt, DiamondDatabaseDirFmt, NCBITaxonomyNodesFormat,
    NCBITaxonomyNamesFormat, NCBITaxonomyBinaryFileFmt, NCBITaxonomyDirFmt,
    EggnogProteinSequencesDirFmt)


plugin.register_semantic_type_to_format(
        ReferenceDB[Eggnog],
        EggnogRefDirFmt)

plugin.register_semantic_type_to_format(ReferenceDB[Diamond],
                                        DiamondDatabaseDirFmt)

plugin.register_semantic_type_to_format(
        ReferenceDB[NCBITaxonomy],
        NCBITaxonomyDirFmt)

plugin.register_semantic_type_to_format(ReferenceDB[EggnogProteinSequences],
                                        EggnogProteinSequencesDirFmt)
