# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from . import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, LociDirectoryFormat,
    SeedOrthologDirFmt, GenomeSequencesDirectoryFormat,
    OrthologAnnotationDirFmt,
)
from ..plugin_setup import plugin
from ..sample_data import SampleData

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

plugin.register_semantic_types(
    GenomeData, Genes, Proteins, Loci, DNASequence, Orthologs, NOG
)

plugin.register_semantic_type_to_format(
    GenomeData[Genes],
    artifact_format=GenesDirectoryFormat
)

plugin.register_semantic_type_to_format(
    GenomeData[Proteins],
    artifact_format=ProteinsDirectoryFormat
)

plugin.register_semantic_type_to_format(
    GenomeData[Loci],
    artifact_format=LociDirectoryFormat
)

plugin.register_semantic_type_to_format(
    GenomeData[Orthologs],
    artifact_format=SeedOrthologDirFmt
)

plugin.register_semantic_type_to_format(
    GenomeData[DNASequence],
    artifact_format=GenomeSequencesDirectoryFormat
)

plugin.register_semantic_type_to_format(
    GenomeData[NOG],
    artifact_format=OrthologAnnotationDirFmt
)

plugin.register_semantic_type_to_format(
    SampleData[Orthologs],
    artifact_format=SeedOrthologDirFmt
)

plugin.register_artifact_class(
    SampleData[NOG],
    directory_format=OrthologAnnotationDirFmt
)
