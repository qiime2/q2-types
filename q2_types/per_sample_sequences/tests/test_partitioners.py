# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import shutil
import tempfile
import gzip
import os

from q2_types.per_sample_sequences._formats import (
    SingleLanePerSamplePairedEndFastqDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt
    )
from q2_types.per_sample_sequences._deferred_setup._partitioners import (
    partition_samples_paired, partition_samples_single
)

from q2_types.per_sample_sequences import (
    FastqGzFormat, FastqManifestFormat)


from qiime2.plugin.testing import TestPluginBase


class PartitionTestingUtils:
    def _compare_fastqs(self, obs_file, exp_file):
        with gzip.open(obs_file) as obs_fh:
            with gzip.open(exp_file) as exp_fh:
                self.assertEqual(exp_fh.read(), obs_fh.read())

    def _compare_manifests(self, act_manifest, exp_manifest):
        # strip comment lines before comparing
        act_manifest = [x for x in act_manifest if not x.startswith('#')]
        self.assertEqual(act_manifest, exp_manifest)


class PairedPartitionersTests(TestPluginBase, PartitionTestingUtils):
    package = "q2_types.per_sample_sequences.tests"

    def setUp(self):
        fp = self.get_data_path('partition-paired')
        self.tempdir = tempfile.TemporaryDirectory()
        for file in os.listdir(fp):
            if file != 'MANIFEST':
                with open(os.path.join(fp, file), 'rb') as fh:
                    with gzip.open(
                        os.path.join(self.tempdir.name, file) + '.gz',
                            'wb') as zipped_fh:
                        shutil.copyfileobj(fh, zipped_fh)
            if file == 'MANIFEST':
                shutil.copyfile(os.path.join(fp, file),
                                os.path.join(self.tempdir.name, file))
        self.demux = SingleLanePerSamplePairedEndFastqDirFmt(self.tempdir.name,
                                                             mode="r")

        super().setUp()

    def tearDown(self):
        self.tempdir.cleanup()
        super().tearDown()

    def test_partition(self):
        partition = partition_samples_paired(self.demux)

        exp_samples_fwd = ('sample1_S1_L001_R1_001.fastq.gz',
                           'sample2_S1_L001_R1_001.fastq.gz',
                           'sample3_S1_L001_R1_001.fastq.gz')
        exp_samples_rev = ('sample1_S1_L001_R2_001.fastq.gz',
                           'sample2_S1_L001_R2_001.fastq.gz',
                           'sample3_S1_L001_R2_001.fastq.gz')

        exp_foward_fastq = [
            view for path, view in
            self.demux.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name
        ]

        exp_reverse_fastq = [
            view for path, view in
            self.demux.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name
        ]

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = \
                ['sample-id,filename,direction\n',
                 f'sample{idx + 1},{exp_samples_fwd[idx]},forward\n',
                 f'sample{idx + 1},{exp_samples_rev[idx]},reverse\n']
            self._compare_manifests(act_manifest, exp_manifest)

            forward_fastq = [
                view for path, view in
                sample.sequences.iter_views(FastqGzFormat)
                if 'R1_001.fastq' in path.name]
            self.assertEqual(len(forward_fastq), 1)

            reverse_fastq = [
                view for path, view in
                sample.sequences.iter_views(FastqGzFormat)
                if 'R2_001.fastq' in path.name]
            self.assertEqual(len(reverse_fastq), 1)

            self._compare_fastqs(
                str(forward_fastq[0]), str(exp_foward_fastq[idx]))
            self._compare_fastqs(
                str(reverse_fastq[0]), str(exp_reverse_fastq[idx]))

    def test_partition_num_specified(self):
        partition = partition_samples_paired(self.demux, 2)
        samples = partition[1]
        act_manifest = list(samples.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample1,sample1_S1_L001_R1_001.fastq.gz,forward\n',
                        'sample1,sample1_S1_L001_R2_001.fastq.gz,reverse\n',
                        'sample2,sample2_S1_L001_R1_001.fastq.gz,forward\n',
                        'sample2,sample2_S1_L001_R2_001.fastq.gz,reverse\n']
        self._compare_manifests(act_manifest, exp_manifest)

        forward_fastq = [
            view for path, view in
            samples.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name]
        self.assertEqual(len(forward_fastq), 2)

        exp_foward_fastq = [
                view for path, view in
                self.demux.sequences.iter_views(FastqGzFormat)
                if 'R1_001.fastq' in path.name]

        self._compare_fastqs(
            str(forward_fastq[0]), str(exp_foward_fastq[0]))
        self._compare_fastqs(
            str(forward_fastq[1]), str(exp_foward_fastq[1]))

        reverse_fastq = [
            view for path, view in
            samples.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]
        self.assertEqual(len(reverse_fastq), 2)
        exp_reverse_fastq = [
            view for path, view in
            self.demux.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]

        self._compare_fastqs(
            str(reverse_fastq[0]), str(exp_reverse_fastq[0]))
        self._compare_fastqs(
            str(reverse_fastq[1]), str(exp_reverse_fastq[1]))

        samples = partition[2]
        act_manifest = list(samples.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample3,sample3_S1_L001_R1_001.fastq.gz,forward\n',
                        'sample3,sample3_S1_L001_R2_001.fastq.gz,reverse\n']
        self._compare_manifests(act_manifest, exp_manifest)

        forward_fastq = [
            view for path, view in
            samples.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name]
        self.assertEqual(len(forward_fastq), 1)

        self._compare_fastqs(
            str(forward_fastq[0]), str(exp_foward_fastq[2]))

        reverse_fastq = [
            view for path, view in
            samples.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]
        self.assertEqual(len(reverse_fastq), 1)

        self._compare_fastqs(
            str(reverse_fastq[0]), str(exp_reverse_fastq[2]))

    def test_partition_more_partitions_than_samples(self):
        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*3.*3"):
            partition = partition_samples_paired(self.demux, 100)

        exp_samples_fwd = ('sample1_S1_L001_R1_001.fastq.gz',
                           'sample2_S1_L001_R1_001.fastq.gz',
                           'sample3_S1_L001_R1_001.fastq.gz')
        exp_samples_rev = ('sample1_S1_L001_R2_001.fastq.gz',
                           'sample2_S1_L001_R2_001.fastq.gz',
                           'sample3_S1_L001_R2_001.fastq.gz')

        exp_foward_fastq = [
            view for path, view in
            self.demux.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name]

        exp_reverse_fastq = [
            view for path, view in
            self.demux.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = \
                ['sample-id,filename,direction\n',
                 f'sample{idx + 1},{exp_samples_fwd[idx]},forward\n',
                 f'sample{idx + 1},{exp_samples_rev[idx]},reverse\n']

            self._compare_manifests(act_manifest, exp_manifest)

            forward_fastq = [
                view for path, view in
                sample.sequences.iter_views(FastqGzFormat)
                if 'R1_001.fastq' in path.name]
            self.assertEqual(len(forward_fastq), 1)

            reverse_fastq = [
                view for path, view in
                sample.sequences.iter_views(FastqGzFormat)
                if 'R2_001.fastq' in path.name]
            self.assertEqual(len(reverse_fastq), 1)

            self._compare_fastqs(
                str(forward_fastq[0]), str(exp_foward_fastq[idx]))
            self._compare_fastqs(
                str(reverse_fastq[0]), str(exp_reverse_fastq[idx]))


class SinglePartitionerTests(TestPluginBase, PartitionTestingUtils):
    package = "q2_types.per_sample_sequences.tests"

    def setUp(self):
        fp = self.get_data_path('partition-single')
        self.tempdir = tempfile.TemporaryDirectory()
        for file in os.listdir(fp):
            if file != 'MANIFEST':
                with open(os.path.join(fp, file), 'rb') as fh:
                    with gzip.open(
                        os.path.join(self.tempdir.name, file) + '.gz',
                            'wb') as zipped_fh:
                        shutil.copyfileobj(fh, zipped_fh)
            if file == 'MANIFEST':
                shutil.copyfile(os.path.join(fp, file),
                                os.path.join(self.tempdir.name, file))
        self.demux = SingleLanePerSampleSingleEndFastqDirFmt(self.tempdir.name,
                                                             mode="r")

        super().setUp()

    def tearDown(self):
        self.tempdir.cleanup()
        return super().tearDown()

    def test_partition(self):

        partition = partition_samples_single(self.demux)

        exp_samples = ('sample1_S1_L001_R1_001.fastq.gz',
                       'sample2_S1_L001_R1_001.fastq.gz',
                       'sample3_S1_L001_R1_001.fastq.gz')

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = ['sample-id,filename,direction\n',
                            f'sample{idx + 1},{exp_samples[idx]},forward\n']
            self._compare_manifests(act_manifest, exp_manifest)

            output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
            self.assertEqual(len(output_fastq), 1)
            exp_fastqs = list(self.demux.sequences.iter_views(FastqGzFormat))
            self._compare_fastqs(str(output_fastq[0][1]),
                                 str(exp_fastqs[idx][1]))

    def test_partition_num_specified(self):
        partition = partition_samples_single(self.demux, 2)

        exp_fastqs = list(self.demux.sequences.iter_views(FastqGzFormat))

        samples = partition[1]
        act_manifest = list(samples.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample1,sample1_S1_L001_R1_001.fastq.gz,forward\n',
                        'sample2,sample2_S1_L001_R1_001.fastq.gz,forward\n']
        self._compare_manifests(act_manifest, exp_manifest)

        output_fastq = list(samples.sequences.iter_views(FastqGzFormat))
        self.assertEqual(len(output_fastq), 2)
        self._compare_fastqs(
            str(output_fastq[0][1]), str(exp_fastqs[0][1]))
        self._compare_fastqs(
            str(output_fastq[1][1]), str(exp_fastqs[1][1]))

        samples = partition[2]
        act_manifest = list(samples.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample3,sample3_S1_L001_R1_001.fastq.gz,forward\n']
        self._compare_manifests(act_manifest, exp_manifest)

        output_fastq = list(samples.sequences.iter_views(FastqGzFormat))
        self.assertEqual(len(output_fastq), 1)
        self._compare_fastqs(
            str(output_fastq[0][1]), str(exp_fastqs[2][1]))

    def test_partition_more_partitions_than_samples(self):

        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*3.*3"):
            partition = partition_samples_single(self.demux, 100)

        exp_samples = ('sample1_S1_L001_R1_001.fastq.gz',
                       'sample2_S1_L001_R1_001.fastq.gz',
                       'sample3_S1_L001_R1_001.fastq.gz')

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = ['sample-id,filename,direction\n',
                            f'sample{idx + 1},{exp_samples[idx]},forward\n']
            self._compare_manifests(act_manifest, exp_manifest)

            output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
            self.assertEqual(len(output_fastq), 1)
            exp_fastqs = list(self.demux.sequences.iter_views(FastqGzFormat))
            self._compare_fastqs(str(output_fastq[0][1]),
                                 str(exp_fastqs[idx][1]))
