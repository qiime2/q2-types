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


# if the format itself specifies the phred offset, that would make it so the
# user doesn't have to provide the metadata.yml. for example, we could have
# FastqWithManifest and FastqWithManifestPhred64.

## based on conversation on 17 March, we're going to go with names like:
##  - SingleEndFastqManifestPhred33
##  - SingleEndFastqManifestPhred64
##  - PairedEndFastqManifestPhred33
##  - PairedEndFastqManifestPhred64
## there will only be a manifest, and it will point to abs or relative paths
## on the file system. the Phred64 formats will convert to Phred33, so that
## internally all data is phred33. side note: update the moving pics tutorial
## data so that it is phred33 on import.
## this should be a FileFormat (not a DirectoryFormat)
class FastqWithManifest(model.DirectoryFormat):
    manifest = model.File('MANIFEST', format=FastqManifestFormat)

    sequences = model.FileCollection(r'.*\.fastq\.gz', format=FastqGzFormat)
    metadata = model.File('metadata.yml', format=YamlFormat)

    # i don't get where this is used or why it's required here - evan, help.
    @sequences.set_path_maker
    def sequences_path_maker(self, sample_id, barcode_id, read_number):
        return '%s_%s_L001_R%d_001.fastq.gz' % \
            (sample_id, barcode_id, read_number)


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
    SingleLanePerSamplePairedEndFastqDirFmt, FastqWithManifest
)
