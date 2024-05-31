# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from qiime2.plugin import SemanticType
from q2_types.plugin_setup import plugin

ReferenceDB = SemanticType('ReferenceDB', field_names='type')
Diamond = SemanticType('Diamond', variant_of=ReferenceDB.field['type'])
Eggnog = SemanticType('Eggnog', variant_of=ReferenceDB.field['type'])
NCBITaxonomy = SemanticType(
    'NCBITaxonomy', variant_of=ReferenceDB.field['type']
    )
EggnogProteinSequences = SemanticType(
    'EggnogProteinSequences', variant_of=ReferenceDB.field['type']
)
aminoHMM = SemanticType(
    'aminoHMM', variant_of=ReferenceDB.field['type']
)
dnaHMM = SemanticType(
    'dnaHMM', variant_of=ReferenceDB.field['type']
)
rnaHMM = SemanticType(
    'rnaHMM', variant_of=ReferenceDB.field['type']
)
aminoHMMpressed = SemanticType(
    'aminoHMMpressed', variant_of=ReferenceDB.field['type']
)
dnaHMMpressed = SemanticType(
    'dnaHMMpressed', variant_of=ReferenceDB.field['type']
)
rnaHMMpressed = SemanticType(
    'rnaHMMpressed', variant_of=ReferenceDB.field['type']
)
plugin.register_semantic_types(
    ReferenceDB, Diamond, Eggnog, NCBITaxonomy, EggnogProteinSequences,
    aminoHMM, dnaHMM, rnaHMM, aminoHMMpressed, rnaHMMpressed, dnaHMMpressed
)
