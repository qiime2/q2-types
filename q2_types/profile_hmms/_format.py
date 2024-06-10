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


class HmmBinaryFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        pass


class BaseHmmPressedDirFmt(model.DirectoryFormat):
    """
    The  <hmmfile>.h3m file contains the profile HMMs
    and their annotation in a binary format. The <hmmfile>.h3i file is an
    SSI index for the <hmmfile>.h3m file.  The <hmmfile>.h3f file contains
    precomputed data structures for the fast heuristic filter
    (the MSV filter).  The <hmmfile>.h3p file contains precomputed data
    structures for the rest of each profile.
    """
    h3m = model.File(r'.*\.hmm\.h3m', format=HmmBinaryFileFmt)
    h3i = model.File(r'.*\.hmm\.h3i', format=HmmBinaryFileFmt)
    h3f = model.File(r'.*\.hmm\.h3f', format=HmmBinaryFileFmt)
    h3p = model.File(r'.*\.hmm\.h3p', format=HmmBinaryFileFmt)


class HmmBaseFileFmt(model.TextFileFormat):
    def _validate_file_fmt(
            self, level: str, alphabet: str, single_profile: bool
    ):
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
                    f"{e}"
                )

            if len(hmm_profiles) > 1 and single_profile:
                raise ValidationError(
                        f"Expected 1 profile, found {len(hmm_profiles)}."
                    )

            for hmm_profile in hmm_profiles[:parse_n_profiles]:
                hmm_profile.validate(tolerance=tolerance)

                if hmm_profile.alphabet.type.lower() != alphabet:
                    raise ValidationError(
                        "Found profile with alphabet "
                        f"{hmm_profile.alphabet.type.lower()}\n"
                        f"{self.__class__} only accepts {alphabet} profiles."
                    )


class ProteinHmmFileFmt(HmmBaseFileFmt):
    alphabet = "amino"

    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, True)


class DnaHmmFileFmt(HmmBaseFileFmt):
    alphabet = "dna"

    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, True)


class RnaHmmFileFmt(HmmBaseFileFmt):
    alphabet = "rna"

    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, True)


ProteinHmmDirectoryFormat = model.SingleFileDirectoryFormat(
    'AminoHmmFileFmt', r'.*\..hmm', ProteinHmmFileFmt)

DnaHmmDirectoryFormat = model.SingleFileDirectoryFormat(
    'DnaHmmFileFmt', r'.*\..hmm', DnaHmmFileFmt)

RnaHmmDirectoryFormat = model.SingleFileDirectoryFormat(
    'RnaHmmFileFmt', r'.*\..hmm', RnaHmmFileFmt)


class ProteinHmmMultipleProfilesFileFmt(ProteinHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, False)


class DnaHmmMultipleProfilesFileFmt(DnaHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, False)


class RnaHmmMultipleProfilesFileFmt(RnaHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(level, self.alphabet, False)


ProteinHmmMultipleProfilesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AminoHmmMultipleProfilesDirectoryFormat',
    r'.*\..hmm',
    ProteinHmmMultipleProfilesFileFmt
)

DnaHmmMultipleProfilesDirectoryFormat = model.SingleFileDirectoryFormat(
    'DnaHmmMultipleProfilesDirectoryFormat',
    r'.*\..hmm',
    DnaHmmMultipleProfilesFileFmt,
)

RnaHmmMultipleProfilesDirectoryFormat = model.SingleFileDirectoryFormat(
    'RnaHmmMultipleProfilesDirectoryFormat',
    r'.*\..hmm',
    RnaHmmMultipleProfilesFileFmt,
)

plugin.register_formats(
    ProteinHmmMultipleProfilesFileFmt,
    DnaHmmMultipleProfilesFileFmt,
    RnaHmmMultipleProfilesFileFmt,
    ProteinHmmMultipleProfilesDirectoryFormat,
    DnaHmmMultipleProfilesDirectoryFormat,
    RnaHmmMultipleProfilesDirectoryFormat,
    ProteinHmmDirectoryFormat, DnaHmmDirectoryFormat, RnaHmmDirectoryFormat
)
