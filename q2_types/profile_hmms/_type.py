# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType
from q2_types.plugin_setup import plugin
from q2_types.profile_hmms._format import (
    PressedProfileHmmsDirectoryFmt,
    DNASingleProfileHmmDirectoryFmt,
    DNAMultipleProfileHmmDirectoryFmt,
    RNASingleProfileHmmDirectoryFmt,
    RNAMultipleProfileHmmDirectoryFmt,
    ProteinSingleProfileHmmDirectoryFmt,
    ProteinMultipleProfileHmmDirectoryFmt
)


ProfileHMM = SemanticType('ProfileHMM', field_names='type')
SingleProtein = SemanticType(
    'SingleProtein', variant_of=ProfileHMM.field['type']
)
SingleDNA = SemanticType(
    'SingleDNA', variant_of=ProfileHMM.field['type']
)
SingleRNA = SemanticType(
    'SingleRNA', variant_of=ProfileHMM.field['type']
)
MultipleProtein = SemanticType(
    'MultipleProtein', variant_of=ProfileHMM.field['type']
)
MultipleDNA = SemanticType(
    'MultipleDNA', variant_of=ProfileHMM.field['type']
)
MultipleRNA = SemanticType(
    'MultipleRNA', variant_of=ProfileHMM.field['type']
)
PressedProtein = SemanticType(
    'PressedProtein', variant_of=ProfileHMM.field['type']
)
PressedDNA = SemanticType(
    'PressedDNA', variant_of=ProfileHMM.field['type']
)
PressedRNA = SemanticType(
    'PressedRNA', variant_of=ProfileHMM.field['type']
)

plugin.register_semantic_types(
    ProfileHMM,
    SingleProtein, SingleDNA, SingleRNA,
    MultipleProtein, MultipleDNA, MultipleRNA,
    PressedProtein, PressedDNA, PressedRNA
)

plugin.register_artifact_class(
    ProfileHMM[PressedProtein],
    directory_format=PressedProfileHmmsDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models for amino acid "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    ProfileHMM[PressedDNA],
    directory_format=PressedProfileHmmsDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models for DNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    ProfileHMM[PressedRNA],
    directory_format=PressedProfileHmmsDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models for RNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    ProfileHMM[SingleProtein],
    directory_format=ProteinSingleProfileHmmDirectoryFmt,
    description=(
        "One single profile Hidden Markov Model representing a group "
        "of related proteins."
    )
)

plugin.register_artifact_class(
    ProfileHMM[SingleDNA],
    directory_format=DNASingleProfileHmmDirectoryFmt,
    description=(
        "One single profile Hidden Markov Model representing a group "
        "of related DNA sequences."
    )
)

plugin.register_artifact_class(
    ProfileHMM[SingleRNA],
    directory_format=RNASingleProfileHmmDirectoryFmt,
    description=(
        "One single profile Hidden Markov Model representing a group "
        "of related RNA sequences."
    )
)

plugin.register_artifact_class(
    ProfileHMM[MultipleProtein],
    directory_format=ProteinMultipleProfileHmmDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models, "
        "each representing a group of related proteins."
    )
)

plugin.register_artifact_class(
    ProfileHMM[MultipleDNA],
    directory_format=DNAMultipleProfileHmmDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models, "
        "each representing a group of related DNA sequences."
    )
)

plugin.register_artifact_class(
    ProfileHMM[MultipleRNA],
    directory_format=RNAMultipleProfileHmmDirectoryFmt,
    description=(
        "A collection of profile Hidden Markov Models, "
        "each representing a group of related RNA sequences."
    )
)
