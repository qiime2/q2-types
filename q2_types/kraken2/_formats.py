# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from collections import defaultdict

import pandas as pd
from pandas.core.dtypes.common import is_string_dtype
from qiime2.plugin import model, ValidationError


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


class FileDictMixin:
    def file_dict(self, relative=False, suffixes=None):
        """
        For per sample directories it returns a mapping of sample id to
        another dictionary where keys represent the file name and values
        correspond to the filepath for each file.
        For files, it returns a mapping of file name to filepath for each
        file. The specified suffixes are removed from filenames.

        Parameters
        ---------
        relative : bool
            Whether to return filepaths relative to the directory's location.
            Returns absolute filepaths by default.
        suffixes : List
            A list of suffixes that should be removed from the filenames to
            generate the ID.

        Returns
        -------
        dict
            Mapping of filename -> filepath as described above.
            Or mapping of sample id -> dict {filename: filepath} as
            described above.
            Both levels of the dictionary are sorted alphabetically by key.
        """
        ids = defaultdict(dict)
        for entry in self.path.iterdir():
            if entry.is_dir():
                outer_id = entry.name
                for path in entry.iterdir():
                    file_path, inner_id = _create_path(
                        path=path,
                        relative=relative,
                        dir_format=self,
                        suffixes=suffixes
                    )

                    ids[outer_id][inner_id] = str(file_path)
                ids[outer_id] = dict(sorted(ids[outer_id].items()))
            else:
                file_path, inner_id = _create_path(
                    path=entry,
                    relative=relative,
                    dir_format=self,
                    suffixes=suffixes

                )

                ids[inner_id] = str(file_path)

        return dict(sorted(ids.items()))


def _create_path(path, relative, dir_format, suffixes):
    """
    This function processes the input file path to generate an absolute or
    relative path string and the ID derived from the file name. The ID is
    extracted by removing the one of the specified suffixes  from the file
    name. If no suffixes are specified the ID is defined to be the filename.

    Parameters:
    ---------
        path : Path
            A Path object representing the file path to process.
        relative : bool
            A flag indicating whether the returned path should be relative
            to the directory formats path or absolute.
        dir_format : DirectoryFormat.
            Any object of class DirectoryFormat.

    Returns:
    -------
        path_dict : str
            The full relative or absolut path to the file.
        _id : str
            The ID derived from the file name. ID will be "" if the filename
            consists only of the suffix.
    """
    file_name = path.stem

    _id = file_name

    if suffixes:
        for suffix in suffixes:
            if file_name.endswith(suffix[1:]):
                _id = file_name[:-len(suffix)]
                break

    path_dict = (
        path.absolute().relative_to(dir_format.path.absolute())
        if relative
        else path.absolute()
    )
    return str(path_dict), _id


class Kraken2ReportDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    reports = model.FileCollection(
        r'.+report\.(txt|tsv)$', format=Kraken2ReportFormat
    )

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


class Kraken2OutputDirectoryFormat(model.DirectoryFormat):
    reports = model.FileCollection(
        r'.+output\.(txt|tsv)$', format=Kraken2OutputFormat
    )

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
