# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from pyhmmer.plan7 import HMMFile
from qiime2.plugin import model
from qiime2.core.exceptions import ValidationError
from q2_types.plugin_setup import plugin


class ProfileHmmBinaryFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        pass


class PressedProfileHmmsDirectoryFmt(model.DirectoryFormat):
    """
    The  <hmmfile>.h3m file contains the profile HMMs
    and their annotation in a binary format. The <hmmfile>.h3i file is an
    SSI index for the <hmmfile>.h3m file.  The <hmmfile>.h3f file contains
    precomputed data structures for the fast heuristic filter
    (the MSV filter).  The <hmmfile>.h3p file contains precomputed data
    structures for the rest of each profile.
    """
    h3m = model.File(r'.*\.hmm\.h3m', format=ProfileHmmBinaryFileFmt)
    h3i = model.File(r'.*\.hmm\.h3i', format=ProfileHmmBinaryFileFmt)
    h3f = model.File(r'.*\.hmm\.h3f', format=ProfileHmmBinaryFileFmt)
    h3p = model.File(r'.*\.hmm\.h3p', format=ProfileHmmBinaryFileFmt)


class ProfileHmmFileFmt(model.TextFileFormat):
    def _validate_(self, level: str):
        """
        Check http://eddylab.org/software/hmmer/Userguide.pdf
        section "HMMER profile HMM files" for full description of
        hmm file format.
        """
        parse_n_profiles = {"min": 3, "max": None}[level]
        tolerance = 0.0001

        with HMMFile(str(self)) as hmm_file:
            try:
                hmm_profiles = list(hmm_file)
            except TypeError as e:
                raise ValidationError(
                    "Found profiles with different alphabets.\n"
                    f"Printing pyhmmer error message: {e}"
                )

            if len(hmm_profiles) > 1 and self.single:
                raise ValidationError(
                        f"Expected 1 profile, found {len(hmm_profiles)}."
                    )

            for hmm_profile in hmm_profiles[:parse_n_profiles]:
                hmm_profile.validate(tolerance=tolerance)

                if hmm_profile.alphabet.type.lower() != self.alphabet:
                    raise ValidationError(
                        "Found profile with alphabet "
                        f"{hmm_profile.alphabet.type.lower()}\n"
                        f"Expected alphabet: {self.alphabet}."
                    )


class ProteinProfileHmmFileFmt(ProfileHmmFileFmt):
    alphabet = "amino"


class ProteinSingleProfileHmmFileFmt(ProteinProfileHmmFileFmt):
    single = True


class ProteinMultipleProfileHmmFileFmt(ProteinProfileHmmFileFmt):
    single = False


class DNAProfileHmmFileFmt(ProfileHmmFileFmt):
    alphabet = "dna"


class DNASingleProfileHmmFileFmt(DNAProfileHmmFileFmt):
    single = True


class DNAMultipleProfileHmmFileFmt(DNAProfileHmmFileFmt):
    single = False


class RNAProfileHmmFileFmt(ProfileHmmFileFmt):
    alphabet = "rna"


class RNASingleProfileHmmFileFmt(RNAProfileHmmFileFmt):
    single = True


class RNAMultipleProfileHmmFileFmt(RNAProfileHmmFileFmt):
    single = False


class ProteinSingleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profile = model.File(r'.*\.hmm', format=ProteinSingleProfileHmmFileFmt)


class ProteinMultipleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profiles = model.File(r'.*\.hmm', format=ProteinMultipleProfileHmmFileFmt)


class DNASingleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profile = model.File(r'.*\.hmm', format=DNASingleProfileHmmFileFmt)


class DNAMultipleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profiles = model.File(r'.*\.hmm', format=DNAMultipleProfileHmmFileFmt)


class RNASingleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profile = model.File(r'.*\.hmm', format=RNASingleProfileHmmFileFmt)


class RNAMultipleProfileHmmDirectoryFmt(model.DirectoryFormat):
    profiles = model.File(r'.*\.hmm', format=RNAMultipleProfileHmmFileFmt)


plugin.register_formats(
    PressedProfileHmmsDirectoryFmt,
    ProteinSingleProfileHmmDirectoryFmt,
    ProteinMultipleProfileHmmDirectoryFmt,
    DNASingleProfileHmmDirectoryFmt,
    DNAMultipleProfileHmmDirectoryFmt,
    RNASingleProfileHmmDirectoryFmt,
    RNAMultipleProfileHmmDirectoryFmt
)
