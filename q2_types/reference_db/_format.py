# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import gzip
import re
from pyhmmer.plan7 import HMMFile
from qiime2.plugin import model
from qiime2.core.exceptions import ValidationError
from q2_types.plugin_setup import plugin
from q2_types.reference_db._type import (
    ReferenceDB, Eggnog, Diamond, NCBITaxonomy, EggnogProteinSequences,
    aminoHMM, dnaHMM, rnaHMM, aminoHMMpressed, rnaHMMpressed, dnaHMMpressed
)
from q2_types.feature_data import MixedCaseProteinFASTAFormat


class EggnogRefTextFileFmt(model.TextFileFormat):
    _expected_columns = [
            '# Taxid',
            'Sci.Name',
            'Rank',
            'Named Lineage',
            'Taxid Lineage'
    ]
    _line_pattern = re.compile(
        r'^\d+\t'  # Taxid
        r'([^\t]*\t)'  # Sci.Name
        r'(no rank|species|subspecies)\t'  # Rank
        r'([^\t]*\t)'  # Named Lineage
        r'\d+(,\d+)*$'  # 'Taxid Lineage'
    )

    def _validate_1st_line(self, line):
        fields = line.strip("\n").split("\t")
        if len(fields) > 5:
            raise ValidationError(
                "Too many columns.\n"
                "Expected columns:\n"
                f"{self._expected_columns}\n"
                "Columns given:\n"
                f"{fields}"
            )

        if not (
            fields[0] == '# Taxid' and
            fields[1] == 'Sci.Name' and
            fields[2] == 'Rank' and
            fields[3] == 'Named Lineage' and
            fields[4] == 'Taxid Lineage'
        ):
            raise ValidationError(
                "Wrong columns.\n"
                "Expected columns:\n"
                f"{self._expected_columns}\n"
                "Columns given:\n"
                f"{fields}"
            )

    def _validate_Nth_line(self, line, line_no):
        if not self._line_pattern.match(line):
            raise ValidationError(
                f"Invalid line at line {line_no}:\n"
                f"{line}"
            )

    def _validate_(self, level):
        with open(str(self), "r") as file:
            line_no = 0
            is_fist_line = True

            for line in file:
                # Validate first line
                if is_fist_line:
                    self._validate_1st_line(line)
                    line_no += 1
                    is_fist_line = False

                # Validate N'th line
                else:
                    self._validate_Nth_line(line, line_no)
                    line_no += 1


class EggnogRefBinFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        pass


plugin.register_formats(EggnogRefTextFileFmt, EggnogRefBinFileFmt)


class EggnogRefDirFmt(model.DirectoryFormat):
    eggnog = model.FileCollection(r'eggnog.*db.*',
                                  format=EggnogRefBinFileFmt)

    @eggnog.set_path_maker
    def eggnog_path_maker(self, name):
        return str(name)


plugin.register_formats(EggnogRefDirFmt)

plugin.register_semantic_type_to_format(
        ReferenceDB[Eggnog],
        EggnogRefDirFmt)


class DiamondDatabaseFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        # TODO: have native diamond validation run on db/self.path
        pass


DiamondDatabaseDirFmt = model.SingleFileDirectoryFormat(
    'DiamondDatabaseDirFmt', 'ref_db.dmnd', DiamondDatabaseFileFmt)

plugin.register_formats(DiamondDatabaseFileFmt, DiamondDatabaseDirFmt)
plugin.register_semantic_type_to_format(ReferenceDB[Diamond],
                                        DiamondDatabaseDirFmt)


class NCBITaxonomyNodesFormat(model.TextFileFormat):
    def _validate_n_records(self, n=None):
        with open(str(self), "r") as fh:
            file_ = enumerate(fh) if n is None else zip(range(n), fh)

            for i, line in file_:
                line = line.rstrip("\n").split("\t|\t")
                if 13 > len(line) or len(line) > 18:
                    raise ValidationError(
                        "NCBI taxonomy nodes file must have 13 columns, "
                        f"found {len(line)} columns on line {i + 1}."
                    )
                if not line[0].isnumeric() or not line[1].isnumeric():
                    raise ValidationError(
                        "NCBI taxonomy nodes file must contain a numeric "
                        "taxonomy ID in the first two columns, found "
                        f"non-numeric value on line {i + 1}."
                    )
                for col in (5, 7, 9, 10, 11):
                    if not line[col].isnumeric() or \
                            not int(line[col]) in (0, 1):
                        raise ValidationError(
                            "NCBI taxonomy nodes file must contain 0 or 1 "
                            "in columns 6, 8, 10, 11, and 12, found a "
                            f"non-allowed value on line {i + 1}, column "
                            f"{col + 1}: {line[col]}."
                        )

    def _validate_(self, level):
        self._validate_n_records(n={"min": 10, "max": None}[level])


class NCBITaxonomyNamesFormat(model.TextFileFormat):
    def _validate_n_records(self, n=None):
        with open(str(self), "r") as fh:
            file_ = enumerate(fh) if n is None else zip(range(n), fh)

            for i, line in file_:
                line = line.rstrip("\n").split("\t|\t")
                if len(line) != 4:
                    raise ValidationError(
                        "NCBI taxonomy names file must have 4 columns, "
                        f"found {len(line)} columns on line {i + 1}."
                    )
                if not line[0].isnumeric():
                    raise ValidationError(
                        "NCBI taxonomy name file must contain a numeric "
                        "taxonomy ID in the first column, found non-numeric "
                        f"value on line {i + 1}: {line[0]}."
                    )

    def _validate_(self, level):
        self._validate_n_records(n={"min": 10, "max": None}[level])


class NCBITaxonomyBinaryFileFmt(model.BinaryFileFormat):
    _accession_regex = re.compile(
        r'[OPQ][0-9][A-Z0-9]{3}[0-9]|'  # UniProt
        r'[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}|'  # UniProt
        r'[A-Z]{3}\d{3,7}|'  # EMBL-EBI
        r'[A-Z]+[-._]?\d+'  # NCBI
    )
    _accession_version_regex = re.compile(
        r'[OPQ][0-9][A-Z0-9]{3}[0-9]\.\d+|'
        r'[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}\.\d+|'
        r'[A-Z]{3}\d{3,7}\.\d+|'
        r'[A-Z]+[-._]?\d+\.\d+'
    )
    _taxid_regex = r'\d{1,10}'
    _gi_regex = r'\d+'
    _line_regex = re.compile(
        rf"^({_accession_regex.pattern})\t"
        rf"({_accession_version_regex.pattern})"
        rf"\t({_taxid_regex})"
        rf"\t({_gi_regex})\n$"
    )

    def _validate_1st_line(self, line: list):
        if not (
            line[0] == "accession" and
            line[1] == "accession.version" and
            line[2] == "taxid" and
            line[3] == "gi"
        ):
            raise ValidationError(
                "NCBI prot.accession2taxid file must have "
                "columns: 'accession', 'accession.version'"
                f", 'taxid' and 'gi'. Got {line} instead."
            )

    def _validate_Nth_line(self, line: list, line_no: int):
        # For every filed validate one record
        splitted_line = line.rstrip("\n").split(sep="\t")

        # Raise exception if the entry does not match pattern
        if not re.match(self._line_regex, line):
            raise ValidationError(
                f"Non-allowed value found in line {line_no}.\n"
                "Printing line:\n"
                f"{splitted_line}"
            )

    def _validate_(self, level):
        with gzip.open(str(self), 'rt') as file:
            # Flag first line
            is_first_line = True
            line_no = 1

            # Set the number of rows to be parsed
            max_lines = {"min": 100, "max": 10000000}[level]

            for line in file:
                # Check time
                if line_no >= max_lines:
                    break

                # Get line and split it into fields
                splitted_line = line.rstrip("\n").split(sep="\t")

                # Check that it is split in 4
                if len(splitted_line) != 4:
                    raise ValidationError(
                        "NCBI prot.accession2taxid file must have 4 columns, "
                        f"found {len(splitted_line)} columns in line "
                        f"{line_no}. \nPrinting line: \n{splitted_line}"
                    )

                # Parse first line
                if is_first_line:
                    self._validate_1st_line(splitted_line)
                    is_first_line = False
                    line_no += 1

                # Parse Nth line
                else:
                    self._validate_Nth_line(line, line_no)
                    line_no += 1


plugin.register_formats(
    NCBITaxonomyNodesFormat, NCBITaxonomyNamesFormat, NCBITaxonomyBinaryFileFmt
    )


class NCBITaxonomyDirFmt(model.DirectoryFormat):
    node = model.File('nodes.dmp', format=NCBITaxonomyNodesFormat)
    names = model.File('names.dmp', format=NCBITaxonomyNamesFormat)
    tax_map = model.File(
        'prot.accession2taxid.gz',
        format=NCBITaxonomyBinaryFileFmt
        )


plugin.register_formats(NCBITaxonomyDirFmt)

plugin.register_semantic_type_to_format(
        ReferenceDB[NCBITaxonomy],
        NCBITaxonomyDirFmt)


class EggnogProteinSequencesDirFmt(model.DirectoryFormat):
    taxid_info = model.File("e5.taxid_info.tsv", format=EggnogRefTextFileFmt)
    proteins = model.File(
        "e5.proteomes.faa", format=MixedCaseProteinFASTAFormat
    )


plugin.register_formats(EggnogProteinSequencesDirFmt)
plugin.register_semantic_type_to_format(ReferenceDB[EggnogProteinSequences],
                                        EggnogProteinSequencesDirFmt)


class HmmBinaryFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        pass


class HmmIdmapFileFmt(model.TextFileFormat):
    def _validate_(self, level):
        with open(str(self), 'r') as file:
            # Set the number of rows to be parsed
            max_lines = {"min": 100, "max": 10000000}[level]
            lines = file.readlines()
            for i, line in enumerate(lines, 1):
                # Check number of lines parsed so far
                if i > max_lines:
                    break

                # Validate line
                if not re.match(r'^(\d+) ([A-Z0-9]+)$', line):
                    raise ValidationError(
                        f"Invalid line {i}.\n"
                        f"{line} \n"
                        "Expected index and an alphanumeric code separated "
                        "by a single space."
                    )

                # Check index is equal to line number
                idx, code = line.rstrip("\n").split(sep=" ")
                if not idx == str(i):
                    raise ValidationError(
                        f"Invalid line {i}.\n"
                        f"{line} \n"
                        f"Expected index {i} but got {idx} instead.\n"
                    )


class BaseHmmPressedDirFmt(model.directory_format):
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
    idmap = model.File(
        r'.*\.hmm\.idmap', format=HmmIdmapFileFmt, optional=True
    )


class AminoHmmPressedDirFmt(BaseHmmPressedDirFmt):
    alphabet = "amino"


class DnaHmmPressedDirFmt(BaseHmmPressedDirFmt):
    alphabet = "dna"


class RnaHmmPressedDirFmt(BaseHmmPressedDirFmt):
    alphabet = "rna"


plugin.register_semantic_type_to_format(
    ReferenceDB[aminoHMMpressed], AminoHmmPressedDirFmt
)

plugin.register_semantic_type_to_format(
    ReferenceDB[dnaHMMpressed], AminoHmmPressedDirFmt
)

plugin.register_semantic_type_to_format(
    ReferenceDB[rnaHMMpressed], AminoHmmPressedDirFmt
)


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
            hmm_profiles = list(hmm_file)

            if len(hmm_profiles) > 1 and single_profile:
                raise ValidationError(
                        f"Expected 1 profile, found {len(hmm_profiles)}."
                    )

            for hmm_profile in hmm_profiles[:parse_n_profiles]:
                hmm_profile.validate(tolerance=tolerance)

                if hmm_profile.alphabet.lower() != alphabet:
                    raise ValidationError(
                        "Found profile with alphabet: "
                        f"{hmm_profile.alph.lower()}\n"
                        f"{self.__class__} only accepts {alphabet} profiles."
                    )


class AminoHmmFileFmt(HmmBaseFileFmt):
    alphabet = "amino"

    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, True)


class DnaHmmFileFmt(HmmBaseFileFmt):
    alphabet = "dna"

    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, True)


class RnaHmmFileFmt(HmmBaseFileFmt):
    alphabet = "rna"

    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, True)


DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'AminoHmmFileFmt', 'profile.hmm', AminoHmmFileFmt)

DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'DnaHmmFileFmt', 'profile.hmm', DnaHmmFileFmt)

DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'RnaHmmFileFmt', 'profile.hmm', RnaHmmFileFmt)

plugin.register_formats(AminoHmmFileFmt, DnaHmmFileFmt, RnaHmmFileFmt)


class HmmAminoDBFileFmt(AminoHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, False)


class HmmDnaDBFileFmt(DnaHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, False)


class HmmRnaDBFileFmt(RnaHmmFileFmt):
    def _validate_(self, level):
        self._validate_file_fmt(self, level, self.alphabet, False)


DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'HmmAminoDBFileFmt', 'profile.hmm', HmmAminoDBFileFmt
)

DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'HmmDnaDBFileFmt', 'profile.hmm', HmmDnaDBFileFmt
)

DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'HmmRnaDBFileFmt', 'profile.hmm', HmmRnaDBFileFmt
)

plugin.register_formats(
    HmmAminoDBFileFmt, HmmDnaDBFileFmt, HmmRnaDBFileFmt
)

plugin.register_semantic_type_to_format(
    ReferenceDB[aminoHMM], HmmAminoDBFileFmt
)

plugin.register_semantic_type_to_format(
    ReferenceDB[dnaHMM], HmmAminoDBFileFmt
)

plugin.register_semantic_type_to_format(
    ReferenceDB[rnaHMM], HmmAminoDBFileFmt
)
