# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import skbio.io
import yaml
import qiime2.plugin.model as model

from ..plugin_setup import plugin


class FastqManifestFormat(model.TextFileFormat):
    """
    Mapping of sample identifiers to filepaths and read direction.

    """
    def sniff(self):
        with self.open() as fh:
            header = fh.readline()
            return header.strip() == 'sample-id,filename,direction'


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
    def sniff(self):
        filepath = str(self)
        sniffer = skbio.io.io_registry.get_sniffer('fastq')
        if sniffer(str(self))[0]:
            try:
                generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                          phred_offset=33, format='fastq',
                                          verify=False)
                for seq, _ in zip(generator, range(15)):
                    pass
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except ValueError:
                pass
        return False


class SingleEndFastqManifestPhred33(model.TextFileFormat):
    def sniff(self):
        first_direction = None
        with self.open() as fh:
            header = fh.readline()
            if header.strip() != 'sample-id,filename,direction':
                return False
            for line in fh:
                line = line.strip()
                if len(line) == 0:
                    continue
                sample_id, path, direction = line.rstrip().split(',')
                if not os.path.exists(os.path.abspath(path)):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)

                if direction not in {'forward', 'reverse'}:
                    raise ValueError('Direction can only be "forward" or '
                                     '"reverse", but found: %s' % direction)

                if first_direction is None:
                    first_direction = direction
                elif first_direction != direction:
                    raise ValueError('Manifest for single-end reads can '
                                     'contain only forward or reverse reads '
                                     'but both are present.')
        return True


class SingleEndFastqManifestPhred64(SingleEndFastqManifestPhred33):
    # the manifest format is the same for the two standard Phred offsets
    pass


class PairedEndFastqManifestPhred33(model.TextFileFormat):

    def sniff(self):
        forward_direction_sample_ids = []
        reverse_direction_sample_ids = []
        with self.open() as fh:
            header = fh.readline()
            if header.strip() != 'sample-id,filename,direction':
                return False
            for line in fh:
                line = line.strip()
                if len(line) == 0:
                    continue
                sample_id, path, direction = line.rstrip().split(',')
                if not os.path.exists(os.path.abspath(path)):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)

                if direction == 'forward':
                    forward_direction_sample_ids.append(sample_id)
                elif direction == 'reverse':
                    reverse_direction_sample_ids.append(sample_id)
                else:
                    raise ValueError('Direction can only be "forward" or '
                                     '"reverse", but found: %s' % direction)

            if sorted(forward_direction_sample_ids) != \
               sorted(reverse_direction_sample_ids):
                # could do some munging here here to make this error message
                # more informative
                raise ValueError('Forward and reverse reads must be provided '
                                 'exactly one time each for each sample.')

        return True


class PairedEndFastqManifestPhred64(PairedEndFastqManifestPhred33):
    # the manifest format is the same for the two standard Phred offsets
    pass


class CasavaOneEightSingleLanePerSampleDirFmt(model.DirectoryFormat):
    sequences = model.FileCollection(
        r'.+_.+_L[0-9][0-9][0-9]_R[12]_001\.fastq\.gz',
        format=FastqGzFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, barcode_id, lane_number,
                             read_number):
        return '%s_%s_L%03d_R%d_001.fastq.gz' % (sample_id, barcode_id,
                                                 lane_number, read_number)


class _SingleLanePerSampleFastqDirFmt(CasavaOneEightSingleLanePerSampleDirFmt):
    manifest = model.File('MANIFEST', format=FastqManifestFormat)
    metadata = model.File('metadata.yml', format=YamlFormat)


class SingleLanePerSampleSingleEndFastqDirFmt(_SingleLanePerSampleFastqDirFmt):
    pass


class SingleLanePerSamplePairedEndFastqDirFmt(_SingleLanePerSampleFastqDirFmt):
    # There is no difference between this and
    # SingleLanePerSampleSingleEndFastqDirFmt (canonically pronounced,
    # SLPSSEFDF) until we have validation.
    pass


plugin.register_formats(
    FastqManifestFormat, YamlFormat, FastqGzFormat,
    CasavaOneEightSingleLanePerSampleDirFmt, _SingleLanePerSampleFastqDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt, SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64, PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64
)
