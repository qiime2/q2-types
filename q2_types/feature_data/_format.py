# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re
import skbio.io

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
import qiime2

from ..plugin_setup import plugin


class TaxonomyFormat(model.TextFileFormat):
    """Legacy format for any 2+ column TSV file, with or without a header.

    This format has been superseded by taxonomy file formats explicitly with
    and without headers, `TSVTaxonomyFormat` and `HeaderlessTSVTaxonomyFormat`,
    respectively.

    This format remains in place for backwards-compatibility. Transformers are
    intentionally not hooked up to transform this format into the canonical
    .qza format (`TSVTaxonomyFormat`) to prevent users from importing data in
    this format. Transformers will remain in place to transform this format
    into in-memory Python objects (e.g. `pd.Series`) so that existing .qza
    files can still be loaded and processed.

    The only header recognized by this format is:

        Feature ID<tab>Taxon

    Optionally followed by other arbitrary columns.

    If this header isn't present, the format is assumed to be headerless.

    This format supports comment lines starting with #, and blank lines.

    """

    def sniff(self):
        with self.open() as fh:
            count = 0
            while count < 10:
                line = fh.readline()

                if line == '':
                    # EOF
                    break
                elif line.lstrip(' ') == '\n':
                    # Blank line
                    continue
                else:
                    cells = line.split('\t')
                    if len(cells) < 2:
                        return False
                    count += 1

            return False if count == 0 else True


TaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TaxonomyDirectoryFormat', 'taxonomy.tsv', TaxonomyFormat)


class HeaderlessTSVTaxonomyFormat(TaxonomyFormat):
    """Format for a 2+ column TSV file without a header.

    This format supports comment lines starting with #, and blank lines.

    """
    pass


HeaderlessTSVTaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'HeaderlessTSVTaxonomyDirectoryFormat', 'taxonomy.tsv',
    HeaderlessTSVTaxonomyFormat)


class TSVTaxonomyFormat(model.TextFileFormat):
    """Format for a 2+ column TSV file with an expected minimal header.

    The only header recognized by this format is:

        Feature ID<tab>Taxon

    Optionally followed by other arbitrary columns.

    This format supports blank lines. The expected header must be the first
    non-blank line. In addition to the header, there must be at least one line
    of data.

    """
    HEADER = ['Feature ID', 'Taxon']

    def _check_n_records(self, n=None):
        with self.open() as fh:
            data_lines = 0
            header = None

            file_ = enumerate(fh) if n is None else zip(range(n), fh)

            for i, line in file_:
                # Tracks line number for error reporting
                i = i + 1

                if line.lstrip(' ') == '\n':
                    # Blank line
                    continue

                cells = line.strip('\n').split('\t')

                if header is None:
                    if cells[:2] != self.HEADER:
                        raise ValidationError("Header row on line {} is "
                                              "invalid. ['Feature ID', "
                                              "'Taxon'] must be the first two "
                                              "header values to be valid."
                                              "\n\nThe first two header "
                                              "values observed are: {}."
                                              .format(i, cells[:2]))
                    header = cells
                else:
                    if len(cells) != len(header):
                        raise ValidationError("Invalid format starting on "
                                              "line {}. Number of columns are "
                                              "not the same as number of "
                                              "header values in the file.\n "
                                              "Header values: {}\nColumn "
                                              "values: {}"
                                              .format(i, header, cells[:]))

                    data_lines += 1

            if data_lines == 0:
                raise ValidationError("No taxonomy records found, only blank "
                                      "lines and/or a header row.")

    def _validate_(self, level):
        self._check_n_records(n={'min': 10, 'max': None}[level])


TSVTaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TSVTaxonomyDirectoryFormat', 'taxonomy.tsv', TSVTaxonomyFormat)


class DNAFASTAFormat(model.TextFileFormat):
    def _validate_lines(self, max_lines):
        FASTADNAValidator = re.compile(r'[ACGTURYKMSWBDHVN]+\r?\n?')
        last_line_was_ID = False

        with open(str(self), 'rb') as fh:
            try:
                first = fh.read(6)
                if first[:3] == b'\xEF\xBB\xBF':
                    first = first[3:]
                # Empty files should validate
                if first.strip() == b'':
                    return
                if first[0] != ord(b'>'):
                    raise ValidationError("First line of file is not a valid "
                                          "FASTA ID. FASTA IDs must start "
                                          "with '>'")
                fh.seek(0)
                for line_number, line in enumerate(fh, 1):
                    if line_number >= max_lines:
                        return
                    line = line.decode('utf-8-sig')
                    if line.startswith('>'):
                        if last_line_was_ID:
                            raise ValidationError('Multiple consecutive IDs '
                                                  'starting on line '
                                                  f'{line_number-1!r}')
                        last_line_was_ID = True
                    elif re.fullmatch(FASTADNAValidator, line):
                        last_line_was_ID = False
                    else:
                        raise ValidationError('Invalid characters on line '
                                              f'{line_number} (does not match '
                                              'IUPAC characters for a DNA '
                                              'sequence).')
            except UnicodeDecodeError as e:
                raise ValidationError(f'utf-8 cannot decode byte on line '
                                      f'{line_number}') from e

    def _validate_(self, max_lines):
        level_map = {'min': 100, 'max': float('inf')}
        self._validate_lines(level_map[max_lines])


DNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'DNASequencesDirectoryFormat', 'dna-sequences.fasta', DNAFASTAFormat)


class PairedDNASequencesDirectoryFormat(model.DirectoryFormat):
    left_dna_sequences = model.File('left-dna-sequences.fasta',
                                    format=DNAFASTAFormat)
    right_dna_sequences = model.File('right-dna-sequences.fasta',
                                     format=DNAFASTAFormat)


class AlignedDNAFASTAFormat(model.TextFileFormat):
    def sniff(self):
        filepath = str(self)
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta', verify=False)
            try:
                initial_length = len(next(generator))
                for seq, _ in zip(generator, range(4)):
                    if len(seq) != initial_length:
                        return False
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except (StopIteration, ValueError):
                pass
        return False


AlignedDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedDNASequencesDirectoryFormat', 'aligned-dna-sequences.fasta',
    AlignedDNAFASTAFormat)


class DifferentialFormat(model.TextFileFormat):
    def validate(self, *args):
        try:
            md = qiime2.Metadata.load(str(self))
        except qiime2.metadata.MetadataFileError as md_exc:
            raise ValidationError(md_exc) from md_exc

        if md.column_count == 0:
            raise ValidationError('Format must contain at least 1 column')

        filtered_md = md.filter_columns(column_type='numeric')
        if filtered_md.column_count != md.column_count:
            raise ValidationError('Must only contain numeric values.')


DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'DifferentialDirectoryFormat', 'differentials.tsv', DifferentialFormat)


plugin.register_formats(
    TSVTaxonomyFormat, TSVTaxonomyDirectoryFormat,
    HeaderlessTSVTaxonomyFormat, HeaderlessTSVTaxonomyDirectoryFormat,
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat,
    DifferentialFormat, DifferentialDirectoryFormat
)
