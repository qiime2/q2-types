# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io
import yaml
import qiime2.plugin.model as model

from ..plugin_setup import plugin


class _FastqManifestBase(model.TextFileFormat):
    """
    Base class for mapping of sample identifiers to filepaths and read
    direction.

    """
    EXPECTED_HEADER = None

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

                cells = line.rstrip('\n').split(',')
                if header is None:
                    if cells != self.EXPECTED_HEADER:
                        return False
                    header = cells
                else:
                    if len(cells) != len(header):
                        return False
                    data_lines += 1

            return header is not None and data_lines > 0


class FastqManifestFormat(_FastqManifestBase):
    """
    Mapping of sample identifiers to relative filepaths and read direction.

    """
    EXPECTED_HEADER = ['sample-id', 'filename', 'direction']


class FastqAbsolutePathManifestFormat(_FastqManifestBase):
    """
    Mapping of sample identifiers to absolute filepaths and read direction.

    """
    EXPECTED_HEADER = ['sample-id', 'absolute-filepath', 'direction']


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
    def sniff(self):
        with self.open() as fh:
            if fh.read(2)[:2] != b'\x1f\x8b':
                return False

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


class MiSeqDemuxDirFmt(model.DirectoryFormat):
    sequences = model.FileCollection(r'.+_.+_R[12]_001\.fastq\.gz',
                                     format=FastqGzFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, barcode_id, read_number):
        return '%s_%s_R%d_001.fastq.gz' % (sample_id, barcode_id, read_number)


plugin.register_formats(
    FastqManifestFormat, YamlFormat, FastqGzFormat,
    CasavaOneEightSingleLanePerSampleDirFmt, MiSeqDemuxDirFmt,
    _SingleLanePerSampleFastqDirFmt, SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt, SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64, PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64
)
