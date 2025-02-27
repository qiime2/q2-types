# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from pandas.core.dtypes.common import is_string_dtype
from qiime2.plugin import model, ValidationError

from q2_types._util import FileDictMixin


class Kraken2ReportFormat(model.TextFileFormat):
    MEASURE_COLUMNS = {
        'perc_frags_covered': float, 'n_frags_covered': int,
        'n_frags_assigned': int
    }

    MINIMIZER_COLUMS = {
        'n_read_minimizers': int,
        'n_uniq_minimizers': int
    }

    TAXA_COLUMNS = {
        'rank': str, 'taxon_id': int, 'name': str
    }

    NORMAL_COLUMNS = {**MEASURE_COLUMNS, **TAXA_COLUMNS}
    ALL_COLUMNS = {**MEASURE_COLUMNS, **MINIMIZER_COLUMS, **TAXA_COLUMNS}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _to_dataframe(self):
        df = pd.read_csv(self.path, sep='\t', header=None)
        if len(df.columns) == len(self.NORMAL_COLUMNS):
            return df, self.NORMAL_COLUMNS
        elif len(df.columns) == len(self.ALL_COLUMNS):
            return df, self.ALL_COLUMNS
        else:
            raise ValueError(
                'Length mismatch: expected 6 or 8 columns, '
                f'found {len(df.columns)}.'
            )

    def _validate_(self, level):
        try:
            df, COLUMNS = self._to_dataframe()
            df.columns = COLUMNS.keys()
        except ValueError as e:
            if 'Length mismatch' in str(e):
                raise ValidationError(str(e))
            else:
                raise ValidationError(
                    'An error occurred when reading in the '
                    'Kraken2 report file'
                ) from e
        for col, dtype in COLUMNS.items():
            if dtype == str and is_string_dtype(df[col]):
                continue
            if df[col].dtype == dtype:
                continue
            raise ValidationError(
                f'Expected {dtype} type in the "{col}" column, '
                f'got {df[col].dtype}'
            )


class Kraken2ReportDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+report\.(txt|tsv)$'
    suffixes = ['.report']
    reports = model.FileCollection(pathspec, format=Kraken2ReportFormat)

    @reports.set_path_maker
    def reports_path_maker(self, sample_id, mag_id=None):
        prefix = f'{sample_id}/{mag_id}_' if mag_id else f'{sample_id}/'
        return f'{prefix}report.txt'


class Kraken2DBReportFormat(Kraken2ReportFormat):
    COLUMNS = {
        'perc_minimizers_covered': float,
        'n_minimizers_covered': int,
        'n_minimizers_assigned': int,
        'rank': str,
        'taxon_id': int,
        'name': str
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _to_dataframe(self):
        num_headers = self._count_headers()
        df = pd.read_csv(
            self.path, sep='\t', header=None, skiprows=num_headers
        )
        if not len(df.columns) == len(self.COLUMNS):
            raise ValueError(
                f'Length mismatch: expected {len(self.COLUMNS)} columns, '
                f'found {len(df.columns)}.'
            )
        return df, self.COLUMNS

    def _count_headers(self):
        '''
        kraken2-inspect adds several headers beginning with '#' which we
        wish to ignore
        '''
        with open(self.path, 'r') as fh:
            lines = fh.readlines()

        headers = filter(lambda line: line[0] == '#', lines)
        return len(list(headers))


Kraken2DBReportDirectoryFormat = model.SingleFileDirectoryFormat(
    'Kraken2DBReportDirectoryFormat', 'report.txt', Kraken2DBReportFormat
)


class Kraken2OutputFormat(model.TextFileFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    COLUMNS = (
        'classification', 'sequence_id', 'taxon_id', 'sequence_length',
        'kmer_mappings'
    )

    def _to_dataframe(self):
        df = pd.read_csv(self.path, sep='\t', header=None)
        return df, self.COLUMNS

    def _validate_(self, level):
        df = pd.read_csv(self.path, sep='\t', header=None)
        if df.shape[1] != 5:
            raise ValidationError(
                f'Expected 5 columns in the Kraken2 output file but '
                f'{df.shape[1]} were found.'
            )
        if not set(df.iloc[:, 0].unique()).issubset({'C', 'U'}):
            raise ValidationError(
                'Expected the first column to contain only "C" or "U" values.'
            )


class Kraken2OutputDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+output\.(txt|tsv)$'
    suffixes = ['.output']
    reports = model.FileCollection(pathspec, format=Kraken2OutputFormat)

    @reports.set_path_maker
    def reports_path_maker(self, sample_id, mag_id=None):
        prefix = f'{sample_id}/{mag_id}_' if mag_id else f'{sample_id}/'
        return f'{prefix}output.txt'


class Kraken2DBFormat(model.TextFileFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _validate_(self, level):
        pass


class Kraken2DBDirectoryFormat(model.DirectoryFormat):
    hash = model.File(r'hash.k2d', format=Kraken2DBFormat)
    opts = model.File(r'opts.k2d', format=Kraken2DBFormat)
    taxo = model.File(r'taxo.k2d', format=Kraken2DBFormat)


class BrackenDBFormat(model.TextFileFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _validate_(self, level):
        pass


class BrackenDBDirectoryFormat(model.DirectoryFormat):
    kmers = model.FileCollection(
        r'database(\d{2,})mers\.kmer_distrib$', format=BrackenDBFormat
    )

    @kmers.set_path_maker
    def kmers_path_maker(self, read_len):
        return f'database{read_len}mers.kmer_distrib'
