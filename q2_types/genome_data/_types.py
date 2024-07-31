# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from q2_types.sample_data import SampleData

GenomeData = SemanticType('GenomeData', field_names='type')
Genes = SemanticType('Genes', variant_of=GenomeData.field['type'])
Proteins = SemanticType('Proteins', variant_of=GenomeData.field['type'])
Loci = SemanticType('Loci', variant_of=GenomeData.field['type'])
Orthologs = SemanticType('Orthologs',
                         variant_of=[GenomeData.field['type'],
                                     SampleData.field['type']])
NOG = SemanticType('NOG', variant_of=[GenomeData.field['type'],
                                      SampleData.field['type']])
DNASequence = SemanticType('DNASequence', variant_of=GenomeData.field['type'])
