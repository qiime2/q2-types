# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import skbio.io
import yaml
import qiime.plugin.model as model


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
        sniffer = skbio.io.io_registry.get_sniffer('fastq')
        return sniffer(str(self))[0]


class QIIME1FastqManifestFormat(model.TextFileFormat):
    def sniff(self):
        with self.open() as fh:
            header = fh.readline()
            return header.strip() == \
                'filename,read_number,lane_number,phred_offset'


class QIIME1DemultiplexedFastqFormat(model.TextFileFormat):
    def sniff(self):
        fastq_sniffer = skbio.io.io_registry.get_sniffer('fastq')
        if fastq_sniffer(str(self))[0]:
            generator = skbio.io.read(str(self), constructor=skbio.DNA,
                                      format='fastq', verify=False,
                                      compression='gzip',
                                      phred_offset=33)
            try:
                for seq, _ in zip(generator, range(5)):
                    if len(seq.metadata['id'].split('_')) == 1:
                        # ids should begin with sample-name_, so if there
                        # should be at least two fields when splitting on
                        # underscores.
                        return False
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except ValueError:
                pass
        else:
            return False


class QIIME1DemultiplexedFastqDirFmt(model.DirectoryFormat):
    sequences = model.FileCollection(r'.+\.fastq\.gz',
                                     format=QIIME1DemultiplexedFastqFormat)
    manifest = model.File('MANIFEST', format=QIIME1FastqManifestFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, basename):
        return '%s.fastq.gz' % basename


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
