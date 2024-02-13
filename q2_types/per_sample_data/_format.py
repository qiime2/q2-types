# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import re
import subprocess

from q2_types.bowtie2 import Bowtie2IndexDirFmt
from q2_types.feature_data import DNAFASTAFormat
from qiime2.core.exceptions import ValidationError
from qiime2.plugin import model

from ..plugin_setup import plugin


# TODO: that's a copy of the _FastqManifestBase from q2-types
# without the direction check. That could potentially be generalised.
class _FastaManifestBase(model.TextFileFormat):
    """
    Base class for mapping of sample and mag identifiers to filepaths.

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

                    records_seen += 1

            if header is None:
                raise ValidationError('No header found, expected: %s.'
                                      % self.EXPECTED_HEADER)

            if records_seen == 0:
                raise ValidationError('No sample records found in manifest, '
                                      'only observed comments, blank lines, '
                                      'and/or a header row.')


class MultiMAGManifestFormat(_FastaManifestBase):
    EXPECTED_HEADER = ['sample-id', 'mag-id', 'filename']
    PATH_HEADER_LABEL = 'filename'

    def _validate_(self, level):
        self._check_n_records(root=str(self.path.parent),
                              n={'min': 10, 'max': None}[level])


class MultiDirValidationMixin:
    def _validate_(self, level):
        for p in self.path.iterdir():
            if not p.is_dir() and p.name not in ['MANIFEST']:
                raise ValidationError(
                    "Files should be organised in per-sample directories")


class MultiFASTADirectoryFormat(MultiDirValidationMixin,
                                model.DirectoryFormat):
    sequences = model.FileCollection(r'.+\.(fa|fasta)$', format=DNAFASTAFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, mag_id):
        # write out with fasta extension, regardless if input was fa or fasta
        return '%s/%s.fasta' % (sample_id, mag_id)


class MultiMAGSequencesDirFmt(MultiFASTADirectoryFormat):
    manifest = model.File('MANIFEST', format=MultiMAGManifestFormat)


class MultiBowtie2IndexDirFmt(MultiDirValidationMixin, Bowtie2IndexDirFmt):
    pass


class ContigSequencesDirFmt(model.DirectoryFormat):
    pathspec = r'[^\.].+_contigs.(fasta|fa)$'

    sequences = model.FileCollection(pathspec, format=DNAFASTAFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id):
        return r'%s_contigs.fasta' % sample_id

    def sample_dict(self, relative=False):
        '''
        Returns a mapping of sample id to filepath for each set of per-sample
        contigs.

        Parameters
        ---------
        relative : bool
            Whether to return filepaths relative to the directory's location.
            Returns absolute filepaths by default.

        Returns
        -------
        dict
            Mapping of sample id -> filepath as described above. Sorted
            alphabetically by key.
        '''
        contigs_pattern = re.compile(self.pathspec)
        ids = {}
        for path in self.path.iterdir():
            if not contigs_pattern.match(path.name):
                continue

            id = path.name.rsplit('_contigs', 1)[0]
            absolute_path = path.absolute()
            if relative:
                ids[id] = str(
                    absolute_path.relative_to(self.path.absolute())
                )
            else:
                ids[id] = str(absolute_path)

        return dict(sorted(ids.items()))


# borrowed from q2-phylogenomics
class BAMFormat(model.BinaryFileFormat):
    def _validate_(self, level):
        cmd = ['samtools', 'quickcheck', '-v', str(self)]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            raise model.ValidationError(
                'samtools quickcheck -v failed on %s' % self.path.name)


# borrowed from q2-phylogenomics
class BAMDirFmt(model.DirectoryFormat):
    bams = model.FileCollection(r'.+\.bam', format=BAMFormat)

    @bams.set_path_maker
    def bams_path_maker(self, sample_id):
        return '%s.bam' % sample_id


class MultiBAMDirFmt(MultiDirValidationMixin, model.DirectoryFormat):
    bams = model.FileCollection(r'.+\/.+\.bam', format=BAMFormat)

    @bams.set_path_maker
    def bams_path_maker(self, sample_id, genome_id):
        return '%s/%s.bam' % sample_id, genome_id


plugin.register_formats(
    MultiFASTADirectoryFormat,
    MultiMAGSequencesDirFmt,
    ContigSequencesDirFmt,
    MultiBowtie2IndexDirFmt,
    BAMDirFmt,
    MultiBAMDirFmt
)
