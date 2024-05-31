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
    MultipleAminoProfilesPressed,
    MultipleDNAProfilesPressed,
    MultipleRNAProfilesPressed,
    BaseHmmPressedDirFmt
)


HMM = SemanticType('HMM', field_names='type')
plugin.register_semantic_type_to_format(
    HMM[MultipleAminoProfilesPressed], BaseHmmPressedDirFmt
)

plugin.register_semantic_type_to_format(
    HMM[MultipleDNAProfilesPressed], BaseHmmPressedDirFmt
)

plugin.register_semantic_type_to_format(
    HMM[MultipleRNAProfilesPressed], BaseHmmPressedDirFmt
)

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
    description=("TODO")
)

plugin.register_artifact_class(
    HMM[SingleDNAProfile],
    directory_format=DnaHmmDirectoryFormat,
    description=("TODO")
)

plugin.register_artifact_class(
    HMM[SingleDNAProfile],
    directory_format=RnaHmmDirectoryFormat,
    description=("TODO")
)

plugin.register_artifact_class(
    HMM[MultipleAminoProfiles],
    directory_format=AminoHmmMultipleProfilesDirectoryFormat,
    description=("TODO")
)

plugin.register_artifact_class(
    HMM[MultipleDNAProfiles],
    directory_format=DnaHmmMultipleProfilesDirectoryFormat,
    description=("TODO")
)

plugin.register_artifact_class(
    HMM[MultipleRNAProfiles],
    directory_format=RnaHmmMultipleProfilesDirectoryFormat,
    description=("TODO")
)
