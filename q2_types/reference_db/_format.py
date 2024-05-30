# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import gzip
import re
from qiime2.plugin import model
from qiime2.core.exceptions import ValidationError
from q2_types.plugin_setup import plugin
from q2_types.reference_db._type import (
    ReferenceDB, Eggnog, Diamond, NCBITaxonomy,
    EggnogProteinSequences, HMMER, HMMERpressed
)
from q2_types.feature_data import (
    MixedCaseProteinFASTAFormat, ProteinFASTAFormat
)


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


class HmmerBinaryFileFmt(model.BinaryFileFormat):
    def _validate_(self, level):
        pass


class HmmerIdmapFileFmt(model.TextFileFormat):
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


class HmmerBaseDirFmt(model.DirectoryFormat):
    fasta_files = model.FileCollection(
        r'.*\.(fa|fasta|faa)$',
        format=ProteinFASTAFormat,
        optional=False,
    )

    @fasta_files.set_path_maker
    def fasta_files_path_maker(self, name):
        return str(name)


class HmmerPressedDirFmt(HmmerBaseDirFmt):
    """
    The  <hmmfile>.h3m file contains the profile HMMs
    and their annotation in a binary format. The <hmmfile>.h3i file is an
    SSI index for the <hmmfile>.h3m file.  The <hmmfile>.h3f file contains
    precomputed data structures for the fast heuristic filter
    (the MSV filter).  The <hmmfile>.h3p file contains precomputed data
    structures for the rest of each profile.
    """
    h3m = model.File(r'.*\.hmm\.h3m', format=HmmerBinaryFileFmt)
    h3i = model.File(r'.*\.hmm\.h3i', format=HmmerBinaryFileFmt)
    h3f = model.File(r'.*\.hmm\.h3f', format=HmmerBinaryFileFmt)
    h3p = model.File(r'.*\.hmm\.h3p', format=HmmerBinaryFileFmt)
    idmap = model.File(
        r'.*\.hmm\.idmap', format=HmmerIdmapFileFmt, optional=True
    )


class HmmFileFmt(model.TextFileFormat):
    alphabets = {
        "AMINO": "ACDEFGHIKLMNPQRSTVWY",
        "DNA": "ACGT",
        "RNA": "ACGU"
    }
    is_valid_value = {
        "HMMER2.0": lambda x: re.match(r"^.+$", x),
        "HMMER3/a": lambda x: re.match(r"^.+$", x),
        "HMMER3/b": lambda x: re.match(r"^.+$", x),
        "HMMER3/c": lambda x: re.match(r"^.+$", x),
        "HMMER3/d": lambda x: re.match(r"^.+$", x),
        "HMMER3/e": lambda x: re.match(r"^.+$", x),
        "HMMER3/f": lambda x: re.match(r"^.+$", x),
        "NAME": lambda x: re.match(r"^\S+$", x),
        "ACC": lambda x: re.match(r"^\w+$", x),
        "DESC": lambda x: re.match(r"^.+$", x),
        "LENG": lambda x: re.match(r"^\d+$", x),
        "MAXL": lambda x: re.match(r"^\d+$", x),
        "ALPH": lambda x: re.match(r"^(amino|DNA|RNA)$", x, re.IGNORECASE),
        "RF": lambda x: re.match(r"^(yes|no)$", x, re.IGNORECASE),
        "MM": lambda x: re.match(r"^(yes|no)$", x, re.IGNORECASE),
        "CONS": lambda x: re.match(r"^(yes|no)$", x, re.IGNORECASE),
        "CS": lambda x: re.match(r"^(yes|no)$", x, re.IGNORECASE),
        "MAP": lambda x: re.match(r"^(yes|no)$", x, re.IGNORECASE),
        "DATE": lambda x: re.match(r"^.+$", x),
        "COM": lambda x: re.match(r"^\d+ \w+$", x),
        "NSEQ": lambda x: re.match(r"^\d+$", x),
        "EFFN": lambda x: re.match(r"^\d+\.?\d+$", x),
        "CKSUM": lambda x: re.match(r"^\d+$", x),
        "GA": lambda x: re.match(r"^(\d+\.?\d+) (\d+\.?\d+)$", x),
        "TC": lambda x: re.match(r"^(\d+\.?\d+) (\d+\.?\d+)$", x),
        "NC": lambda x: re.match(r"^(\d+\.?\d+) (\d+\.?\d+)$", x),
        "STATS": lambda x: re.match(
            r"^LOCAL (MSV|VITERBI|FORWARD) (\d+\.?\d+) (\d+\.?\d+)$", x
        ),
        "HMM": lambda x: re.match(r"^.+$", x),
        "COMPO": lambda x: re.match(r"^(\d+\.?\d+ ?)+$", x),
    }

    def _parse_header(self, lines):
        tag_values = {}
        for line in lines:
            tag, value = (re.split(r"\s+", line, 1))
            tag_values[tag] = value

        # check that all mandatory tags are present
        mandatory_tags = {"NAME", "LENG", "ALPH", "HMM"}
        HMMER_tags = {[
            f"HMMER{i}"
            for i in ["3/a", "3/b", "3/c", "3/d", "3/e", "3/f", "2.0"]
        ]}
        tags_in_header = tag_values.keys()
        if not (
            mandatory_tags.issubset(tags_in_header) and
            len(HMMER_tags.intersection(tags_in_header)) == 1
        ):
            raise ValidationError(
                "Missing tag(s) in header: \n"
                f"{mandatory_tags.difference(tags_in_header)} \n"
                "Printing lines: \n"
                f"{lines}"
            )

        for tag, value in tag_values.items():
            if not self.is_valid_value[tag](value):
                raise ValidationError(
                    f"Invalid value '{value}' for tag '{tag}'\n"
                    "Printing lines: \n"
                    f"{lines}"
                )

        # Validate alphabet
        expected_alph = self.alphabets[tag_values["ALPH"].upper()]
        observed_alph = "".join(re.split(r"\s+", tag_values["HMM"]))
        if observed_alph != expected_alph:
            raise ValidationError(
                f"Invalid alphabet."
                f"Expected: {self.alph}\n"
                f"Observed: {observed_alph}\n"
            )

        # Save alphabet length
        self.alph_len = len(observed_alph)

    def _parse_body(self):
        """
        Parse the HMMER profile section of the file
        """

    def _validate_(self, level):
        """
        Check http://eddylab.org/software/hmmer/Userguide.pdf
        section "HMMER profile HMM files" for full description of
        hmm file format.
        """

        with open(str(self), 'r') as file:
            # Check if hmm file has more than one profile
            profiles_found = 0
            parse_n_profiles = 1
            for line in file:
                if line.startswith("//"):
                    profiles_found += 1
                    if profiles_found > 1:
                        # If more than one profile is found use level to set
                        # the number of profiles to parse
                        parse_n_profiles = {"min": 3, "max": 300000}[level]
                        break

            # Reset cursor to beginning of file
            file.seek(0)

            # Parse
            profiles_parsed = 0
            while profiles_parsed < parse_n_profiles:
                # Validate header
                header = []
                for line in file:
                    header.append(line)
                    if line.startswith("HMM"):
                        break
                self._parse_header(header)

                # Consume column headers for the state transition probability
                # fields
                observed_headers = set(re.split(r"\s+", file.readline()))
                expected_headers = {
                    "m->m", "m->i", "m->d", "i->m", "i->i", "d->m", "d->d"
                }
                if observed_headers != expected_headers:
                    raise ValidationError(
                        f"Invalid headers."
                        f"Expected: {expected_headers}\n"
                        f"Observed: {observed_headers}\n"
                    )

                # Validate HMMER model
                body = []
                for line in file:
                    if line.startswith("//"):
                        break
                    else:
                        body.append(line)
                self._parse_body(body)

                # Increase count of parsed profiles
                profiles_parsed += 1


class HmmerDirFmt(HmmerBaseDirFmt):
    """
    One or more HMMER profile files.
    """
    hmm_files = model.FileCollection(
        r'.*\.(hmm)$', format=HmmFileFmt
    )

    @hmm_files.set_path_maker
    def hmm_files_path_maker(self, name):
        return str(name)


plugin.register_formats(HmmerDirFmt, HmmerPressedDirFmt)
plugin.register_semantic_type_to_format(ReferenceDB[HMMER],
                                        HmmerDirFmt)
plugin.register_semantic_type_to_format(ReferenceDB[HMMERpressed],
                                        HmmerPressedDirFmt)
