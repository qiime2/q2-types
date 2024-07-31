# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from q2_types.sample_data import SampleData

from .. import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, LociDirectoryFormat,
    GFF3Format, OrthologFileFmt, SeedOrthologDirFmt,
    GenomeSequencesDirectoryFormat, OrthologAnnotationDirFmt,
    GenomeData, Genes, Proteins, Loci, Orthologs, DNASequence, NOG)

from ...plugin_setup import plugin

plugin.register_formats(
    GenesDirectoryFormat, ProteinsDirectoryFormat, LociDirectoryFormat,
    GenomeSequencesDirectoryFormat, OrthologFileFmt, SeedOrthologDirFmt,
    OrthologAnnotationDirFmt, GFF3Format
)

plugin.register_semantic_types(
    GenomeData, Genes, Proteins, Loci, DNASequence, Orthologs, NOG
)

plugin.register_artifact_class(
    GenomeData[Genes],
    directory_format=GenesDirectoryFormat
)

plugin.register_artifact_class(
    GenomeData[Proteins],
    directory_format=ProteinsDirectoryFormat
)

plugin.register_artifact_class(
    GenomeData[Loci],
    directory_format=LociDirectoryFormat
)

plugin.register_artifact_class(
    GenomeData[Orthologs],
    directory_format=SeedOrthologDirFmt
)

plugin.register_artifact_class(
    GenomeData[DNASequence],
    directory_format=GenomeSequencesDirectoryFormat
)

plugin.register_artifact_class(
    GenomeData[NOG],
    directory_format=OrthologAnnotationDirFmt
)

plugin.register_artifact_class(
    SampleData[Orthologs],
    directory_format=SeedOrthologDirFmt
)

plugin.register_artifact_class(
    SampleData[NOG],
    directory_format=OrthologAnnotationDirFmt
)

importlib.import_module('._transformers', __name__)
