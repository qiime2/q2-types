# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from .. import (
    TaxonomyFormat, TaxonomyDirectoryFormat, HeaderlessTSVTaxonomyFormat,
    HeaderlessTSVTaxonomyDirectoryFormat, TSVTaxonomyFormat,
    TSVTaxonomyDirectoryFormat, DNAFASTAFormat, DNASequencesDirectoryFormat,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat,
    AlignedDNASequencesDirectoryFormat, DifferentialFormat,
    DifferentialDirectoryFormat, FASTAFormat,
    AlignedProteinSequencesDirectoryFormat, ProteinSequencesDirectoryFormat,
    MixedCaseProteinSequencesDirectoryFormat,
    MixedCaseAlignedProteinSequencesDirectoryFormat,
    ProteinFASTAFormat, AlignedProteinFASTAFormat, MixedCaseProteinFASTAFormat,
    MixedCaseAlignedProteinFASTAFormat, RNASequencesDirectoryFormat,
    RNAFASTAFormat, AlignedRNAFASTAFormat, AlignedRNASequencesDirectoryFormat,
    PairedRNASequencesDirectoryFormat, BLAST6Format, BLAST6DirectoryFormat,
    MixedCaseDNAFASTAFormat, MixedCaseDNASequencesDirectoryFormat,
    MixedCaseRNAFASTAFormat, MixedCaseRNASequencesDirectoryFormat,
    MixedCaseAlignedDNAFASTAFormat,
    MixedCaseAlignedDNASequencesDirectoryFormat,
    MixedCaseAlignedRNAFASTAFormat,
    MixedCaseAlignedRNASequencesDirectoryFormat,
    SequenceCharacteristicsDirectoryFormat,
    SequenceCharacteristicsFormat,
    FeatureData, Taxonomy, Sequence, PairedEndSequence, AlignedSequence,
    Differential, ProteinSequence, AlignedProteinSequence, RNASequence,
    AlignedRNASequence, PairedEndRNASequence, BLAST6, SequenceCharacteristics)

from ...plugin_setup import plugin


plugin.register_formats(
    TSVTaxonomyFormat, TSVTaxonomyDirectoryFormat,
    HeaderlessTSVTaxonomyFormat, HeaderlessTSVTaxonomyDirectoryFormat,
    TaxonomyFormat, TaxonomyDirectoryFormat, FASTAFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat,
    DifferentialFormat, DifferentialDirectoryFormat, ProteinFASTAFormat,
    AlignedProteinFASTAFormat, MixedCaseProteinFASTAFormat,
    MixedCaseAlignedProteinFASTAFormat, ProteinSequencesDirectoryFormat,
    AlignedProteinSequencesDirectoryFormat,
    MixedCaseProteinSequencesDirectoryFormat,
    MixedCaseAlignedProteinSequencesDirectoryFormat, RNAFASTAFormat,
    RNASequencesDirectoryFormat, AlignedRNAFASTAFormat,
    AlignedRNASequencesDirectoryFormat, PairedRNASequencesDirectoryFormat,
    BLAST6Format, BLAST6DirectoryFormat, MixedCaseDNAFASTAFormat,
    MixedCaseDNASequencesDirectoryFormat, MixedCaseRNAFASTAFormat,
    MixedCaseRNASequencesDirectoryFormat, MixedCaseAlignedDNAFASTAFormat,
    MixedCaseAlignedDNASequencesDirectoryFormat,
    MixedCaseAlignedRNAFASTAFormat,
    MixedCaseAlignedRNASequencesDirectoryFormat, SequenceCharacteristicsFormat,
    SequenceCharacteristicsDirectoryFormat
)

plugin.register_semantic_types(FeatureData, Taxonomy, Sequence,
                               PairedEndSequence, AlignedSequence,
                               Differential, ProteinSequence,
                               AlignedProteinSequence, RNASequence,
                               AlignedRNASequence, PairedEndRNASequence,
                               BLAST6, SequenceCharacteristics)

plugin.register_artifact_class(
    FeatureData[Taxonomy],
    directory_format=TSVTaxonomyDirectoryFormat,
    description=("Hierarchical metadata or annotations associated with a set "
                 "of features. This can contain one or more hierarchical "
                 "levels, and annotations can be anything (e.g., taxonomy of "
                 "organisms, functional categorization of gene families, ...) "
                 "as long as it is strictly hierarchical."))

plugin.register_artifact_class(
    FeatureData[Sequence],
    directory_format=DNASequencesDirectoryFormat,
    description=("Unaligned DNA sequences associated with a set of feature "
                 "identifiers (e.g., ASV sequences or OTU representative "
                 "sequence). Exactly one sequence is associated with each "
                 "feature identifier."))

plugin.register_artifact_class(
    FeatureData[RNASequence],
    directory_format=RNASequencesDirectoryFormat,
    description=("Unaligned RNA sequences associated with a set of feature "
                 "identifiers. Exactly one sequence is associated with each "
                 "feature identifier."))

plugin.register_artifact_class(
    FeatureData[PairedEndSequence],
    directory_format=PairedDNASequencesDirectoryFormat)

plugin.register_artifact_class(
    FeatureData[PairedEndRNASequence],
    directory_format=PairedRNASequencesDirectoryFormat)

plugin.register_artifact_class(
    FeatureData[AlignedSequence],
    directory_format=AlignedDNASequencesDirectoryFormat,
    description=("Aligned DNA sequences associated with a set of feature "
                 "identifiers (e.g., aligned ASV sequences or OTU "
                 "representative sequence). Exactly one sequence is "
                 "associated with each feature identifier."))

plugin.register_artifact_class(
    FeatureData[AlignedRNASequence],
    directory_format=AlignedRNASequencesDirectoryFormat,
    description=("Aligned RNA sequences associated with a set of feature "
                 "identifiers. Exactly one sequence is associated with each "
                 "feature identifier."))

plugin.register_artifact_class(
    FeatureData[Differential], DifferentialDirectoryFormat)

plugin.register_artifact_class(
    FeatureData[ProteinSequence],
    directory_format=ProteinSequencesDirectoryFormat,
    description=("Unaligned protein sequences associated with a set of "
                 "feature identifiers. Exactly one sequence is associated "
                 "with each feature identifier."))

plugin.register_artifact_class(
    FeatureData[AlignedProteinSequence],
    directory_format=AlignedProteinSequencesDirectoryFormat,
    description=("Aligned protein sequences associated with a set of "
                 "feature identifiers. Exactly one sequence is associated "
                 "with each feature identifier."))

# FeatureData[BLAST6] seems to fix file type with semantic type.
plugin.register_artifact_class(
    FeatureData[BLAST6],
    directory_format=BLAST6DirectoryFormat,
    description=("BLAST results associated with a set of feature "
                 "identifiers."))

plugin.register_artifact_class(
    FeatureData[SequenceCharacteristics],
    directory_format=SequenceCharacteristicsDirectoryFormat,
    description=("Characteristics of sequences (e.g., the length of a gene "
                 "in basepairs)."))

importlib.import_module('._transformers', __name__)
importlib.import_module('._validators', __name__)
