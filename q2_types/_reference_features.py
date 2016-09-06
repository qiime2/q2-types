# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType
import qiime.plugin.model as model
from .plugin_setup import plugin
from ._feature_data import (DNAFASTAFormat, AlignedDNAFASTAFormat,
                            TaxonomyFormat)
from ._tree import NewickFormat


ReferenceFeatures = SemanticType('ReferenceFeatures', field_names='type')
SSU = SemanticType('SSU', variant_of=ReferenceFeatures.field['type'])


# Formats
class ReferenceFeaturesDirectoryFormat(model.DirectoryFormat):
    dna_sequences = model.File('dna-sequences.fasta', format=DNAFASTAFormat)
    aligned_dna_sequences = model.File('aligned-dna-sequences.fasta',
                                       format=AlignedDNAFASTAFormat)
    taxonomy = model.File('taxonomy.tsv', format=TaxonomyFormat)
    tree = model.File('tree.nwk', format=NewickFormat)


# Registrations
plugin.register_semantic_type(ReferenceFeatures)
plugin.register_semantic_type(SSU)

plugin.register_semantic_type_to_format(
    ReferenceFeatures[SSU],
    artifact_format=ReferenceFeaturesDirectoryFormat)
