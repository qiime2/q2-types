# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from .. import (
    ProteinMultipleProfileHmmFileFmt,
    ProteinSingleProfileHmmFileFmt,
    RNAMultipleProfileHmmFileFmt,
    RNASingleProfileHmmFileFmt,
    DNAMultipleProfileHmmFileFmt,
    DNASingleProfileHmmFileFmt,
    PressedProfileHmmsDirectoryFmt,
    ProteinSingleProfileHmmDirectoryFmt,
    ProteinMultipleProfileHmmDirectoryFmt,
    DNASingleProfileHmmDirectoryFmt,
    DNAMultipleProfileHmmDirectoryFmt,
    RNASingleProfileHmmDirectoryFmt,
    RNAMultipleProfileHmmDirectoryFmt,
    ProfileHMM,
    SingleProtein, SingleDNA, SingleRNA,
    MultipleProtein, MultipleDNA, MultipleRNA,
    PressedRNA, PressedDNA, PressedProtein
)

from ...plugin_setup import plugin

plugin.register_formats(
    ProteinMultipleProfileHmmFileFmt,
    ProteinSingleProfileHmmFileFmt,
    RNAMultipleProfileHmmFileFmt,
    RNASingleProfileHmmFileFmt,
    DNAMultipleProfileHmmFileFmt,
    DNASingleProfileHmmFileFmt,
    PressedProfileHmmsDirectoryFmt,
    ProteinSingleProfileHmmDirectoryFmt,
    ProteinMultipleProfileHmmDirectoryFmt,
    DNASingleProfileHmmDirectoryFmt,
    DNAMultipleProfileHmmDirectoryFmt,
    RNASingleProfileHmmDirectoryFmt,
    RNAMultipleProfileHmmDirectoryFmt
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
