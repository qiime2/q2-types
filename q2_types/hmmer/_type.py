# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType
from q2_types.plugin_setup import plugin
from q2_types.hmmer._format import (
    AminoHmmMultipleProfilesDirectoryFormat,
    DnaHmmMultipleProfilesDirectoryFormat,
    RnaHmmMultipleProfilesDirectoryFormat,
    AminoHmmDirectoryFormat, DnaHmmDirectoryFormat, RnaHmmDirectoryFormat,
    BaseHmmPressedDirFmt
)


HMM = SemanticType('HMM', field_names='type')
SingleAmino = SemanticType(
    'SingleAmino', variant_of=HMM.field['type']
)
SingleDNA = SemanticType(
    'SingleDNA', variant_of=HMM.field['type']
)
SingleRNA = SemanticType(
    'SingleRNA', variant_of=HMM.field['type']
)
MultipleAmino = SemanticType(
    'MultipleAmino', variant_of=HMM.field['type']
)
MultipleDNA = SemanticType(
    'MultipleDNA', variant_of=HMM.field['type']
)
MultipleRNA = SemanticType(
    'MultipleRNA', variant_of=HMM.field['type']
)
MultipleAminoPressed = SemanticType(
    'MultipleAminoPressed', variant_of=HMM.field['type']
)
MultipleDNAPressed = SemanticType(
    'MultipleDNAPressed', variant_of=HMM.field['type']
)
MultipleRNAPressed = SemanticType(
    'MultipleRNAPressed', variant_of=HMM.field['type']
)

plugin.register_semantic_types(
    HMM,
    SingleAmino, SingleDNA, SingleRNA,
    MultipleAmino, MultipleDNA, MultipleRNA,
    MultipleAminoPressed, MultipleDNAPressed,
    MultipleRNAPressed
)

plugin.register_artifact_class(
    HMM[MultipleAminoPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for amino acid "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    HMM[MultipleDNAPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for DNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    HMM[MultipleRNAPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for RNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    HMM[SingleAmino],
    directory_format=AminoHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related proteins."
    )
)

plugin.register_artifact_class(
    HMM[SingleDNA],
    directory_format=DnaHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related DNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[SingleRNA],
    directory_format=RnaHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related RNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[MultipleAmino],
    directory_format=AminoHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related proteins."
    )
)

plugin.register_artifact_class(
    HMM[MultipleDNA],
    directory_format=DnaHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related DNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[MultipleRNA],
    directory_format=RnaHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related RNA sequences."
    )
)
