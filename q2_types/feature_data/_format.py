# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import numpy as np
import pandas as pd
import skbio.io
import qiime2
import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
import arviz as az
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
    def sniff(self):
        filepath = str(self)
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta', verify=False)
            try:
                for seq, _ in zip(generator, range(5)):
                    pass
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except ValueError:
                pass

        # Empty files are ok also
        empty_sniffer = skbio.io.io_registry.get_sniffer('<emptyfile>')
        return empty_sniffer(filepath)[0]


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

        md = md.to_dataframe()
        if len(md.columns) == 0:
                raise ValueError(
                        ('Differential format must contain'
                         'at least 1 column')
                )


        types = md.dtypes
        for t in types:
            if not np.issubdtype(t, np.number):
                raise ValueError(
                        ('Differential types must only contain '
                         'continuously valued quantities')
                )


        for c in md.columns:
            if (np.isinf(md[c].values).sum() > 0 or
                pd.isnull(md[c]).sum() > 0):
                raise ValueError(
                        ('Differential contains infs or nans.')
                )


DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'DifferentialDirectoryFormat', 'differentials.tsv', DifferentialFormat)


class MonteCarloTensorFormat(model.BinaryFileFormat):

    def sniff(self):
        try:
            az.InferenceData.from_netcdf(str(self))
            return True
        except Exception:
            return False


MonteCarloTensorDirectoryFormat = model.SingleFileDirectoryFormat(
    'MonteCarloTensorDirectoryFormat', 'monte-carlo-samples.az',
    MonteCarloTensorFormat)


plugin.register_formats(
    TSVTaxonomyFormat, TSVTaxonomyDirectoryFormat,
    HeaderlessTSVTaxonomyFormat, HeaderlessTSVTaxonomyDirectoryFormat,
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat,
    DifferentialFormat, DifferentialDirectoryFormat,
    MonteCarloTensorFormat, MonteCarloTensorDirectoryFormat
)
