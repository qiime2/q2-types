# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import gzip
import itertools
import collections
import pathlib

import pandas as pd
import skbio
import skbio.io
import yaml
import qiime2
import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

from ..plugin_setup import plugin
from ._util import (
    _parse_casava_filename,
    _manifest_to_df,
)


class FastqAbsolutePathManifestFormatV2(model.TextFileFormat):
    """
    Base class for mapping of sample identifies to filepaths. This format
    relies heavily on the qiime2.Metadata on-disk format, as well as the
    validation rules and behavior.
    """
    METADATA_COLUMNS = None

    def _validate_(self, level):
        try:
            md = qiime2.Metadata.load(str(self))
        except qiime2.metadata.MetadataFileError as md_exc:
            raise ValidationError(md_exc) from md_exc

        md = md.filter_columns(column_type='categorical')

        md_cols = dict()
        for column in self.METADATA_COLUMNS.keys():
            try:
                md_cols[column] = md.get_column(column)
            except ValueError as md_exc:
                raise ValidationError(md_exc) from md_exc

        filepaths = dict()
        for column_name, column in md_cols.items():
            column = column.to_series()
            for i, (id_, fp) in enumerate(column.iteritems(), start=1):
                # QIIME 2 represents empty cells as np.nan once normalized
                if pd.isna(fp):
                    raise ValidationError(
                        'Missing filepath on line %d and column "%s".'
                        % (i, column_name))
                if not os.path.exists(os.path.expandvars(fp)):
                    raise ValidationError(
                        'Filepath on line %d and column "%s" could not '
                        'be found (%s) for sample "%s".'
                        % (i, column_name, fp, id_))
                if fp in filepaths:
                    old_id, old_col_name, old_row = filepaths[fp]
                    raise ValidationError(
                        'Filepath on line %d and column "%s" (sample "%s") '
                        'has already been registered on line %d and column '
                        '"%s" (sample "%s").'
                        % (i, column_name, id_, old_row, old_col_name, old_id))
                else:
                    filepaths[fp] = (id_, column_name, i)


class _SingleEndFastqManifestV2(FastqAbsolutePathManifestFormatV2):
    METADATA_COLUMNS = {'absolute-filepath': 'forward'}


class SingleEndFastqManifestPhred33V2(_SingleEndFastqManifestV2):
    pass


class SingleEndFastqManifestPhred64V2(_SingleEndFastqManifestV2):
    pass


class _PairedEndFastqManifestV2(FastqAbsolutePathManifestFormatV2):
    METADATA_COLUMNS = {'forward-absolute-filepath': 'forward',
                        'reverse-absolute-filepath': 'reverse'}


class PairedEndFastqManifestPhred33V2(_PairedEndFastqManifestV2):
    pass


class PairedEndFastqManifestPhred64V2(_PairedEndFastqManifestV2):
    pass


class _FastqManifestBase(model.TextFileFormat):
    """
    Base class for mapping of sample identifiers to filepaths and read
    direction.

    """
    EXPECTED_HEADER = None
    PATH_HEADER_LABEL = None

    def _check_n_records(self, root, n=None):
        with self.open() as fh:
            header = None
            records_seen = 0
            file_ = enumerate(fh) if n is None else zip(range(n), fh)
            for i, line in file_:
                i = i + 1  # For easier reporting
                if line.lstrip(' ') == '\n':
                    continue  # Blank line
                elif line.startswith('#'):
                    continue  # Comment line

                cells = [c.strip() for c in line.rstrip('\n').split(',')]
                if header is None:
                    if cells != self.EXPECTED_HEADER:
                        raise ValidationError(
                            'Found header on line %d with the following '
                            'labels: %s, expected: %s'
                            % (i, cells, self.EXPECTED_HEADER))
                    else:
                        header = cells
                else:
                    if len(cells) != len(header):
                        raise ValidationError(
                            'Line %d has %s cells (%s), expected %s.'
                            % (i, len(cells), cells, len(header)))

                    # Structure checks out, so let's make lookup easy
                    cells = dict(zip(header, cells))

                    # TODO: a bunch of tests in this subpackage aren't well
                    # behaved --- many tests fail on this check because the
                    # test data isn't constructed correctly. As well, there
                    # appear to be framework-related issues preventing us from
                    # making this kind of validation work for the relative
                    # manifest formats at this time.
                    if root == '':
                        fp = os.path.join(root, cells[self.PATH_HEADER_LABEL])
                        if not os.path.exists(os.path.expandvars(fp)):
                            raise ValidationError(
                                'File referenced on line %d could not be '
                                'found (%s).'
                                % (i, fp))

                    if cells['direction'] not in ('forward', 'reverse'):
                        raise ValidationError(
                            'Read direction declared on line %d was %s, '
                            'expected `forward` or `reverse`.'
                            % (i, cells['direction']))

                    records_seen += 1

            if header is None:
                raise ValidationError('No header found, expected: %s.'
                                      % self.EXPECTED_HEADER)

            if records_seen == 0:
                raise ValidationError('No sample records found in manifest, '
                                      'only observed comments, blank lines, '
                                      'and/or a header row.')


class FastqManifestFormat(_FastqManifestBase):
    """
    Mapping of sample identifiers to relative filepaths and read direction.

    """
    EXPECTED_HEADER = ['sample-id', 'filename', 'direction']
    PATH_HEADER_LABEL = 'filename'

    def _validate_(self, level):
        self._check_n_records(root=str(self.path.parent),
                              n={'min': 10, 'max': None}[level])


class FastqAbsolutePathManifestFormat(_FastqManifestBase):
    """
    Mapping of sample identifiers to absolute filepaths and read direction.

    """
    EXPECTED_HEADER = ['sample-id', 'absolute-filepath', 'direction']
    PATH_HEADER_LABEL = 'absolute-filepath'

    def _validate_(self, level):
        # This is effectively only invoked on import, so let's just
        # validate the whole file!
        self._check_n_records(root='', n=None)


class SingleEndFastqManifestPhred33(FastqAbsolutePathManifestFormat):
    pass


class SingleEndFastqManifestPhred64(FastqAbsolutePathManifestFormat):
    pass


class PairedEndFastqManifestPhred33(FastqAbsolutePathManifestFormat):
    pass


class PairedEndFastqManifestPhred64(FastqAbsolutePathManifestFormat):
    pass


class YamlFormat(model.TextFileFormat):
    """
    Arbitrary yaml-formatted file.

    """
    def sniff(self):
        with self.open() as fh:
            try:
                yaml.safe_load(fh)
            except yaml.YAMLError:
                return False
        return True


class FastqGzFormat(model.BinaryFileFormat):
    """
    A gzipped fastq file.

    """

    def _check_n_records(self, n=None):
        with gzip.open(str(self), mode='rt', encoding='ascii') as fh:
            zipper = itertools.zip_longest(*[fh] * 4)
            if n is None:
                file_ = enumerate(zipper)
            else:
                file_ = zip(range(1, n), zipper)
            for i, record in file_:
                header, seq, sep, qual = record

                if not header.startswith('@'):
                    raise ValidationError('Header on line %d is not FASTQ, '
                                          'records may be misaligned' %
                                          (i * 4 + 1))

                if seq is None or seq == '\n':
                    raise ValidationError('Missing sequence for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif not seq.isupper():
                    raise ValidationError('Lowercase case sequence on line %d'
                                          % (i * 4 + 2))

                if sep is None:
                    raise ValidationError('Missing separator for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif not sep.startswith('+'):
                    raise ValidationError('Invalid separator on line %d'
                                          % (i * 4 + 3))

                if qual is None:
                    raise ValidationError('Missing quality for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif len(qual) != len(seq):
                    raise ValidationError('Quality score length doesn\'t '
                                          'match sequence length for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))

    def _validate_(self, level):
        with self.open() as fh:
            if fh.peek(2)[:2] != b'\x1f\x8b':
                raise ValidationError('File is uncompressed')

        record_count_map = {'min': 5, 'max': None}
        self._check_n_records(record_count_map[level])


class CasavaOneEightSingleLanePerSampleDirFmt(model.DirectoryFormat):
    _CHECK_PAIRED = True
    _REQUIRE_PAIRED = False

    sequences = model.FileCollection(
        r'.+_.+_L[0-9][0-9][0-9]_R[12]_001\.fastq\.gz',
        format=FastqGzFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, barcode_id, lane_number,
                             read_number):
        return '%s_%s_L%03d_R%d_001.fastq.gz' % (sample_id, barcode_id,
                                                 lane_number, read_number)

    def _find_duplicates(self, ids):
        return {x for x, c in collections.Counter(ids).items() if c > 1}

    @property
    def manifest(self):
        tmp_manifest = FastqManifestFormat()
        with tmp_manifest.open() as fh:
            fh.write('sample-id,filename,direction\n')
            for fp, _ in self.sequences.iter_views(FastqGzFormat):
                sample_id, _, _, _, direction = _parse_casava_filename(fp)
                fh.write('%s,%s,%s\n' % (sample_id, fp.name, direction))

        df = _manifest_to_df(tmp_manifest, self.path.parent)

        if 'reverse' not in df:
            df['reverse'] = None

        if 'forward' not in df:
            df['forward'] = None

        def munge_fn_closure(val):
            if val is not None:
                return str(self.path / pathlib.Path(val).name)
            return val

        for column in {'forward', 'reverse'}:
            df[column] = df[column].apply(munge_fn_closure)

        return df

    def _validate_(self, level):
        forwards = []
        reverse = []
        for p in self.path.iterdir():
            if p.is_dir():
                # This branch happens if you have a filepath that looks roughly
                # like: Human_Kneecap/S1_L001_R1_001.fastq.gz
                # This technically matches the regex. It's easier to just
                # check that there aren't any directories, than making a very
                # complicated regex. This also produces a nicer error anyways.
                d = p.relative_to(self.path)
                raise ValidationError("Contains a subdirectory: %s" % d)
            else:
                if p.name.endswith('_001.fastq.gz'):
                    sample_id = p.name.rsplit('_', maxsplit=4)[0]
                    if p.name.endswith('R1_001.fastq.gz'):
                        forwards.append(sample_id)
                    else:
                        reverse.append(sample_id)

        set_forwards = set(forwards)
        set_reverse = set(reverse)

        if len(set_forwards) != len(forwards):
            raise ValidationError('Duplicate samples in forward reads: %r'
                                  % self._find_duplicates(forwards))
        if len(set_reverse) != len(reverse):
            raise ValidationError('Duplicate samples in reverse reads: %r'
                                  % self._find_duplicates(reverse))

        if forwards and reverse:
            if not self._CHECK_PAIRED:
                raise ValidationError("Forward and reverse reads found.")
            elif set_forwards ^ set_reverse:
                raise ValidationError(
                    "These samples do not have matching pairs of forward and "
                    "reverse reads: %r" % (set_forwards ^ set_reverse))
        elif self._REQUIRE_PAIRED:
            raise ValidationError("Reads are not paired end.")


class _SingleLanePerSampleFastqDirFmt(CasavaOneEightSingleLanePerSampleDirFmt):
    manifest = model.File('MANIFEST', format=FastqManifestFormat)
    metadata = model.File('metadata.yml', format=YamlFormat)


class SingleLanePerSampleSingleEndFastqDirFmt(_SingleLanePerSampleFastqDirFmt):
    _CHECK_PAIRED = False


class SingleLanePerSamplePairedEndFastqDirFmt(_SingleLanePerSampleFastqDirFmt):
    _REQUIRE_PAIRED = True


class CasavaOneEightLanelessPerSampleDirFmt(model.DirectoryFormat):
    sequences = model.FileCollection(r'.+_.+_R[12]_001\.fastq\.gz',
                                     format=FastqGzFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, barcode_id, read_number):
        return '%s_%s_R%d_001.fastq.gz' % (sample_id, barcode_id, read_number)


class QIIME1DemuxFormat(model.TextFileFormat):
    """QIIME 1 demultiplexed FASTA format.

    The QIIME 1 demultiplexed FASTA format is the default output format of
    ``split_libraries.py`` and ``split_libraries_fastq.py``. The file output by
    QIIME 1 is named ``seqs.fna``; this filename is sometimes associated with
    the file format itself due to its widespread usage in QIIME 1.

    The format is documented here:
    http://qiime.org/documentation/file_formats.html#demultiplexed-sequences

    Format details:

    - FASTA file with exactly two lines per record: header and sequence. Each
      sequence must span exactly one line and cannot be split across multiple
      lines.

    - The ID in each header must follow the format ``<sample-id>_<seq-id>``.
      ``<sample-id>`` is the identifier of the sample the sequence belongs to,
      and ``<seq-id>`` is an identifier for the sequence *within* its sample.
      In QIIME 1, ``<seq-id>`` is typically an incrementing integer starting
      from zero, but any non-empty value can be used here, as long as the
      header IDs remain unique throughout the file. Note: ``<sample-id>`` may
      contain sample IDs that contain underscores; the rightmost underscore
      will used to delimit sample and sequence IDs.

    - Descriptions in headers are permitted and ignored.

    - Header IDs must be unique within the file.

    - Each sequence must be DNA and cannot be empty.

    """

    def sniff(self):
        with self.open() as filehandle:
            try:
                self._validate(filehandle, num_records=30)
            except Exception:
                return False
            else:
                return True

    # The code is structured such that `_validate` can be used to validate as
    # much of the file as desired. Users may be able to control levels of
    # validation in the future, and we'll also have the ability to describe
    # *why* a file is invalid. Sniffers can only offer a boolean response
    # currently, but the below `Exceptions` could include real error messages
    # in the future. For now, the `Exceptions` are only used to give a boolean
    # response to the sniffer.
    def _validate(self, filehandle, *, num_records):
        ids = set()
        for (header, seq), _ in zip(itertools.zip_longest(*[filehandle] * 2),
                                    range(num_records)):
            if header is None or seq is None:
                # Not exactly two lines per record.
                raise Exception()

            header = header.rstrip('\n')
            seq = seq.rstrip('\n')

            id = self._parse_id(header)
            if id in ids:
                # Duplicate header ID.
                raise Exception()

            self._validate_id(id)
            self._validate_seq(seq)

            ids.add(id)

    def _parse_id(self, header):
        if not header.startswith('>'):
            raise Exception()
        header = header[1:]

        id = ''
        if header and not header[0].isspace():
            id = header.split(maxsplit=1)[0]
        return id

    def _validate_id(self, id):
        pieces = id.rsplit('_', maxsplit=1)
        if len(pieces) != 2 or not all(pieces):
            raise Exception()

    def _validate_seq(self, seq):
        if seq:
            # Will raise a `ValueError` on invalid DNA characters.
            skbio.DNA(seq, validate=True)
        else:
            # Empty sequence.
            raise Exception()


QIIME1DemuxDirFmt = model.SingleFileDirectoryFormat(
    'QIIME1DemuxDirFmt', 'seqs.fna', QIIME1DemuxFormat)


plugin.register_formats(
    FastqManifestFormat, YamlFormat, FastqGzFormat,
    CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    _SingleLanePerSampleFastqDirFmt, SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt, SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64, PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64, SingleEndFastqManifestPhred33V2,
    SingleEndFastqManifestPhred64V2, PairedEndFastqManifestPhred33V2,
    PairedEndFastqManifestPhred64V2, QIIME1DemuxFormat, QIIME1DemuxDirFmt
)
