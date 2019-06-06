# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re
import io
import math

import skbio.io
import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

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
                elif line.startswith('#'):
                    # Comment line
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

    This format supports comment lines starting with #, and blank lines. The
    expected header must be the first non-comment, non-blank line. In addition
    to the header, there must be at least one line of data.

    """
    HEADER = ['Feature ID', 'Taxon']

    def sniff(self):
        with self.open() as fh:
            data_lines = 0
            header = None
            while data_lines < 10:
                line = fh.readline()

                if line == '':
                    # EOF
                    break
                elif line.lstrip(' ') == '\n':
                    # Blank line
                    continue
                elif line.startswith('#'):
                    # Comment line
                    continue

                cells = line.rstrip('\n').split('\t')
                if header is None:
                    if cells[:2] != self.HEADER:
                        return False
                    header = cells
                else:
                    if len(cells) != len(header):
                        return False
                    data_lines += 1

            return header is not None and data_lines > 0


TSVTaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TSVTaxonomyDirectoryFormat', 'taxonomy.tsv', TSVTaxonomyFormat)


class DNAFASTAFormat(model.TextFileFormat):
    def _check(self, level):
        FASTADNAValidator = re.compile(r'[ACGTURYKMSWBDHVN\-\.]+\n?')
        last_line_was_ID = False

        with open(str(self)) as fh:
            try:
                line_number = 1
                # If we read 2 and only get one \n we have only one \n in the
                # file
                first = fh.read(2)
                # Empty files should pass
                if first == '\n' or first == '':
                    return
                if first[0] != '>':
                    raise ValidationError(
                        "First line of file is not a valid FASTA ID. FASTA "
                        "IDs must start with '>'")
                fh.seek(0)
                line = fh.readline()
                while line != '' and line_number < level:
                    if line.startswith('>'):
                        if last_line_was_ID:
                            raise ValidationError(
                                'Multiple consecutive IDs starting on line '
                                f'{line_number-1!r}')
                        last_line_was_ID = True
                    elif re.fullmatch(FASTADNAValidator, line):
                        last_line_was_ID = False
                    else:
                        raise ValidationError(
                            f'Invalid sequence on line {line_number}')
                    line_number += 1
                    line = fh.readline()
            except UnicodeDecodeError as e:
                # We tell() on the buffer because we want the actual buffer the
                # error occured in, tell() on the file handle will report being
                # at the end of the last buffer when the error occured well
                # into the next buffer
                buffer = fh.buffer
                pos = buffer.tell()
                # We want to start our read from the beginning of the buffer we
                # encountered the error on because we have yet to count any
                # lines in that buffer
                pos = (math.ceil(pos / io.DEFAULT_BUFFER_SIZE) - 1) * \
                    io.DEFAULT_BUFFER_SIZE
                buffer.seek(pos)
                # e.start reports the position of the bad byte in the current
                # buffer not the file, this is the cause of all the pain
                # determining which buffer in the file the error occured in so
                # we can find the bad byte's position in the file not just the
                # buffer. If the bad byte is the final byte in a buffer it will
                # report it as being the first byte in the next buffer. This is
                # likely due to the fact that e.start reports the buffer
                # position of the bad byte, and e.end reports the buffer
                # position of the next good byte. If the last byte in a buffer
                # is bad then e.start should be 8192 and e.end should be byte 0
                # of the next buffer, but end being less than start doesn't
                # really make sense, so this is handled by bumping e.start to 0
                # and e.end to 1
                fh_error = io.TextIOWrapper(io.BytesIO(buffer.read(e.start)),
                                            errors='ignore')
                # We need to count the lines in the buffer the error occured in
                # only counting newline terminated lines to ensure we do not
                # double count the line the error occured on, the line count is
                # initialized to one which accounts for the error line, and the
                # error line will always terminate with the bad byte not a
                # newline
                for line in fh_error:
                    if line[-1] == '\n':
                        line_number += 1
                raise ValidationError('Unicode cannot decode byte on line '
                                      f'{line_number}') from e

    def _validate_(self, level):
        level_map = {'min': 100, 'max': float('inf')}
        self._check(level_map[level])


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


plugin.register_formats(
    TSVTaxonomyFormat, TSVTaxonomyDirectoryFormat,
    HeaderlessTSVTaxonomyFormat, HeaderlessTSVTaxonomyDirectoryFormat,
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat
)
