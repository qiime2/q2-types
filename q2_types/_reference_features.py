# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import types

import skbio
import skbio.io
import pandas as pd

from qiime.plugin import SemanticType, DataLayout
from .plugin_setup import plugin
from ._feature_data import (DNAFASTAFormat, AlignedDNAFASTAFormat,
                            TaxonomyFormat, taxonomy_to_pandas_series,
                            dna_sequences_to_generator,
                            aligned_dna_sequences_to_tabular_msa)
from ._tree import NewickFormat, tree_to_skbio_tree_node


ReferenceFeatures = SemanticType('ReferenceFeatures', field_names='type')
SSU = SemanticType('SSU', variant_of=ReferenceFeatures.field['type'])

reference_features_data_layout = DataLayout('reference-features', 1)
reference_features_data_layout.register_file('dna-sequences.fasta',
                                             DNAFASTAFormat)
reference_features_data_layout.register_file('aligned-dna-sequences.fasta',
                                             AlignedDNAFASTAFormat)
reference_features_data_layout.register_file('taxonomy.tsv', TaxonomyFormat)
reference_features_data_layout.register_file('tree.nwk', NewickFormat)

plugin.register_data_layout(reference_features_data_layout)
plugin.register_data_layout_reader('reference-features', 1, pd.Series,
                                   taxonomy_to_pandas_series)
plugin.register_data_layout_reader('reference-features', 1,
                                   types.GeneratorType,
                                   dna_sequences_to_generator)
plugin.register_data_layout_reader('reference-features', 1,
                                   skbio.TabularMSA,
                                   aligned_dna_sequences_to_tabular_msa)
plugin.register_data_layout_reader('reference-features', 1, skbio.TreeNode,
                                   tree_to_skbio_tree_node)

plugin.register_semantic_type(ReferenceFeatures)
plugin.register_semantic_type(SSU)

plugin.register_type_to_data_layout(ReferenceFeatures[SSU],
                                    'reference-features', 1)
