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
SingleAminoProfile = SemanticType(
    'SingleAminoProfile', variant_of=HMM.field['type']
)
SingleDNAProfile = SemanticType(
    'SingleDNAProfile', variant_of=HMM.field['type']
)
SingleRNAProfile = SemanticType(
    'SingleRNAProfile', variant_of=HMM.field['type']
)
MultipleAminoProfiles = SemanticType(
    'MultipleAminoProfiles', variant_of=HMM.field['type']
)
MultipleDNAProfiles = SemanticType(
    'MultipleDNAProfiles', variant_of=HMM.field['type']
)
MultipleRNAProfiles = SemanticType(
    'MultipleRNAProfiles', variant_of=HMM.field['type']
)
MultipleAminoProfilesPressed = SemanticType(
    'MultipleAminoProfilesPressed', variant_of=HMM.field['type']
)
MultipleDNAProfilesPressed = SemanticType(
    'MultipleDNAProfilesPressed', variant_of=HMM.field['type']
)
MultipleRNAProfilesPressed = SemanticType(
    'MultipleRNAProfilesPressed', variant_of=HMM.field['type']
)
plugin.register_artifact_class(
    HMM[MultipleAminoProfilesPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for amino acid "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    HMM[MultipleDNAProfilesPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for DNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_artifact_class(
    HMM[MultipleRNAProfilesPressed],
    directory_format=BaseHmmPressedDirFmt,
    description=(
        "A collection of Hidden Markov Model profiles for RNA "
        "sequences in binary format and indexed."
    )
)

plugin.register_semantic_types(
    HMM,
    SingleAminoProfile, SingleDNAProfile, SingleRNAProfile,
    MultipleAminoProfiles, MultipleDNAProfiles, MultipleRNAProfiles,
    MultipleAminoProfilesPressed, MultipleDNAProfilesPressed,
    MultipleRNAProfilesPressed
)

plugin.register_artifact_class(
    HMM[SingleAminoProfile],
    directory_format=AminoHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related proteins."
    )
)

plugin.register_artifact_class(
    HMM[SingleDNAProfile],
    directory_format=DnaHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related DNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[SingleRNAProfile],
    directory_format=RnaHmmDirectoryFormat,
    description=(
        "One single Hidden Markov Model profile, representing a group "
        "of related RNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[MultipleAminoProfiles],
    directory_format=AminoHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related proteins."
    )
)

plugin.register_artifact_class(
    HMM[MultipleDNAProfiles],
    directory_format=DnaHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related DNA sequences."
    )
)

plugin.register_artifact_class(
    HMM[MultipleRNAProfiles],
    directory_format=RnaHmmMultipleProfilesDirectoryFormat,
    description=(
        "A collection of Hidden Markov Model profiles, each representing a "
        "group of related RNA sequences."
    )
)
