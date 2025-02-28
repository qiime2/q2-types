# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
import pandas as pd

import qiime2

from q2_types.multiplexed_sequences import (
    BarcodePairedSequenceFastqIterator, BarcodeSequenceFastqIterator)

from q2_demux import (emp_paired, emp_single,
                      partition_samples_paired, partition_samples_single)

from q2_types.per_sample_sequences import (
    FastqGzFormat, FastqManifestFormat)

from q2_demux.tests.test_demux import EmpTestingUtils


class singlePartitionersTests(unittest.TestCase, EmpTestingUtils):

    def setUp(self):
        self.barcodes = [('@s1/2 abc/2', 'AAAA', '+', 'YYYY'),
                         ('@s2/2 abc/2', 'TTAA', '+', 'PPPP'),
                         ('@s3/2 abc/2', 'AACC', '+', 'PPPP'),
                         ('@s4/2 abc/2', 'TTAA', '+', 'PPPP'),
                         ('@s5/2 abc/2', 'AACC', '+', 'PPPP'),
                         ('@s6/2 abc/2', 'AAAA', '+', 'PPPP'),
                         ('@s7/2 abc/2', 'CGGC', '+', 'PPPP'),
                         ('@s8/2 abc/2', 'GGAA', '+', 'PPPP'),
                         ('@s9/2 abc/2', 'CGGC', '+', 'PPPP'),
                         ('@s10/2 abc/2', 'CGGC', '+', 'PPPP'),
                         ('@s11/2 abc/2', 'GGAA', '+', 'PPPP')]

        golaybarcodes = [  # ATGATGCGACCA -> ACGATGCGACCA
                         ('@s1/2 abc/2', 'ATGATGCGACCA', '+', 'YYYYYYYYYYYY'),
                         ('@s2/2 abc/2', 'AGCTATCCACGA', '+', 'PPPPPPPPPPPP'),
                         ('@s3/2 abc/2', 'ACACACTATGGC', '+', 'PPPPPPPPPPPP'),
                         ('@s4/2 abc/2', 'AGCTATCCACGA', '+', 'PPPPPPPPPPPP'),
                         ('@s5/2 abc/2', 'ACACACTATGGC', '+', 'PPPPPPPPPPPP'),
                         ('@s6/2 abc/2', 'ACGATGCGACCA', '+', 'PPPPPPPPPPPP'),
                         # CATTGTATCAAC -> CATCGTATCAAC
                         ('@s7/2 abc/2', 'CATTGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s8/2 abc/2', 'CTAACGCAGGGG', '+', 'PPPPPPPPPPPP'),
                         ('@s9/2 abc/2', 'CATCGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s10/2 abc/2', 'CATCGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s11/2 abc/2', 'CTAACGCAGTCA', '+', 'PPPPPPPPPPPP')]

        self.forward = [('@s1/1 abc/1', 'GGG', '+', 'YYY'),
                        ('@s2/1 abc/1', 'CCC', '+', 'PPP'),
                        ('@s3/1 abc/1', 'AAA', '+', 'PPP'),
                        ('@s4/1 abc/1', 'TTT', '+', 'PPP'),
                        ('@s5/1 abc/1', 'ATA', '+', 'PPP'),
                        ('@s6/1 abc/1', 'TAT', '+', 'PPP'),
                        ('@s7/1 abc/1', 'CGC', '+', 'PPP'),
                        ('@s8/1 abc/1', 'GCG', '+', 'PPP'),
                        ('@s9/1 abc/1', 'ACG', '+', 'PPP'),
                        ('@s10/1 abc/1', 'GCA', '+', 'PPP'),
                        ('@s11/1 abc/1', 'TGA', '+', 'PPP')]

        self.reverse = [('@s1/1 abc/1', 'CCC', '+', 'YYY'),
                        ('@s2/1 abc/1', 'GGG', '+', 'PPP'),
                        ('@s3/1 abc/1', 'TTT', '+', 'PPP'),
                        ('@s4/1 abc/1', 'AAA', '+', 'PPP'),
                        ('@s5/1 abc/1', 'TAT', '+', 'PPP'),
                        ('@s6/1 abc/1', 'ATA', '+', 'PPP'),
                        ('@s7/1 abc/1', 'GCG', '+', 'PPP'),
                        ('@s8/1 abc/1', 'CGC', '+', 'PPP'),
                        ('@s9/1 abc/1', 'CGT', '+', 'PPP'),
                        ('@s10/1 abc/1', 'TGC', '+', 'PPP'),
                        ('@s11/1 abc/1', 'TCA', '+', 'PPP')]

        self.bpsi = BarcodePairedSequenceFastqIterator(
            self.barcodes, self.forward, self.reverse)

        barcode_map = pd.Series(
            ['AAAA', 'AACC', 'TTAA', 'GGAA', 'CGGC'], name='bc',
            index=pd.Index(['sample1', 'sample2', 'sample3',
                            'sample4', 'sample5'], name='id')
        )
        self.barcode_map = qiime2.CategoricalMetadataColumn(barcode_map)

        self.bpsi_werr = BarcodePairedSequenceFastqIterator(golaybarcodes,
                                                            self.forward,
                                                            self.reverse)

        golay_barcode_map = pd.Series(
            ['ACGATGCGACCA', 'ACACACTATGGC', 'AGCTATCCACGA',
             'CTAACGCAGTCA', 'CATCGTATCAAC'], name='bc',
            index=pd.Index(['sample1', 'sample2', 'sample3', 'sample4',
                            'sample5'], name='id')
        )
        self.golay_barcode_map = qiime2.CategoricalMetadataColumn(
            golay_barcode_map)

    def test_partition(self):
        demux, _ = emp_paired(self.bpsi, self.barcode_map,
                              golay_error_correction=False)

        partition = partition_samples_paired(demux)

        exp_samples_fwd = ('sample1_1_L001_R1_001.fastq.gz',
                           'sample2_3_L001_R1_001.fastq.gz',
                           'sample3_2_L001_R1_001.fastq.gz',
                           'sample4_5_L001_R1_001.fastq.gz',
                           'sample5_4_L001_R1_001.fastq.gz')
        exp_samples_rev = ('sample1_1_L001_R2_001.fastq.gz',
                           'sample2_3_L001_R2_001.fastq.gz',
                           'sample3_2_L001_R2_001.fastq.gz',
                           'sample4_5_L001_R2_001.fastq.gz',
                           'sample5_4_L001_R2_001.fastq.gz')
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

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

            self._validate_sample_fastq(
                forward_fastq[0].open(), self.forward, exp_indices[idx])
            self._validate_sample_fastq(
                reverse_fastq[0].open(), self.reverse, exp_indices[idx])

    def test_partition_num_specified(self):
        demux, _ = emp_paired(self.bpsi, self.barcode_map,
                              golay_error_correction=False)
        partition = partition_samples_paired(demux, 2)
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

        sample = partition[1]
        act_manifest = list(sample.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample1,sample1_1_L001_R1_001.fastq.gz,forward\n',
                        'sample1,sample1_1_L001_R2_001.fastq.gz,reverse\n',
                        'sample2,sample2_3_L001_R1_001.fastq.gz,forward\n',
                        'sample2,sample2_3_L001_R2_001.fastq.gz,reverse\n',
                        'sample3,sample3_2_L001_R1_001.fastq.gz,forward\n',
                        'sample3,sample3_2_L001_R2_001.fastq.gz,reverse\n']
        self._compare_manifests(act_manifest, exp_manifest)

        forward_fastq = [
            view for path, view in
            sample.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name]
        self.assertEqual(len(forward_fastq), 3)

        self._validate_sample_fastq(
            forward_fastq[0].open(), self.forward, exp_indices[0])
        self._validate_sample_fastq(
            forward_fastq[1].open(), self.forward, exp_indices[1])
        self._validate_sample_fastq(
            forward_fastq[2].open(), self.forward, exp_indices[2])

        reverse_fastq = [
            view for path, view in
            sample.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]
        self.assertEqual(len(reverse_fastq), 3)

        self._validate_sample_fastq(
            reverse_fastq[0].open(), self.reverse, exp_indices[0])
        self._validate_sample_fastq(
            reverse_fastq[1].open(), self.reverse, exp_indices[1])
        self._validate_sample_fastq(
            reverse_fastq[2].open(), self.reverse, exp_indices[2])

        sample = partition[2]
        act_manifest = list(sample.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample4,sample4_5_L001_R1_001.fastq.gz,forward\n',
                        'sample4,sample4_5_L001_R2_001.fastq.gz,reverse\n',
                        'sample5,sample5_4_L001_R1_001.fastq.gz,forward\n',
                        'sample5,sample5_4_L001_R2_001.fastq.gz,reverse\n']
        self._compare_manifests(act_manifest, exp_manifest)

        forward_fastq = [
            view for path, view in
            sample.sequences.iter_views(FastqGzFormat)
            if 'R1_001.fastq' in path.name]
        self.assertEqual(len(forward_fastq), 2)

        self._validate_sample_fastq(
            forward_fastq[0].open(), self.forward, exp_indices[3])
        self._validate_sample_fastq(
            forward_fastq[1].open(), self.forward, exp_indices[4])

        reverse_fastq = [
            view for path, view in
            sample.sequences.iter_views(FastqGzFormat)
            if 'R2_001.fastq' in path.name]
        self.assertEqual(len(reverse_fastq), 2)

        self._validate_sample_fastq(
            reverse_fastq[0].open(), self.reverse, exp_indices[3])
        self._validate_sample_fastq(
            reverse_fastq[1].open(), self.reverse, exp_indices[4])

    def test_partition_more_partitions_than_samples(self):
        demux, _ = emp_paired(self.bpsi, self.barcode_map,
                              golay_error_correction=False)

        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*5.*5"):
            partition = partition_samples_paired(demux, 100)

        exp_samples_fwd = ('sample1_1_L001_R1_001.fastq.gz',
                           'sample2_3_L001_R1_001.fastq.gz',
                           'sample3_2_L001_R1_001.fastq.gz',
                           'sample4_5_L001_R1_001.fastq.gz',
                           'sample5_4_L001_R1_001.fastq.gz')
        exp_samples_rev = ('sample1_1_L001_R2_001.fastq.gz',
                           'sample2_3_L001_R2_001.fastq.gz',
                           'sample3_2_L001_R2_001.fastq.gz',
                           'sample4_5_L001_R2_001.fastq.gz',
                           'sample5_4_L001_R2_001.fastq.gz')
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

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

            self._validate_sample_fastq(
                forward_fastq[0].open(), self.forward, exp_indices[idx])
            self._validate_sample_fastq(
                reverse_fastq[0].open(), self.reverse, exp_indices[idx])


class pairedPartitionerTests(unittest.TestCase, EmpTestingUtils):
    def setUp(self):
        barcodes = [('@s1/2 abc/2', 'AAAA', '+', 'YYYY'),
                    ('@s2/2 abc/2', 'TTAA', '+', 'PPPP'),
                    ('@s3/2 abc/2', 'AACC', '+', 'PPPP'),
                    ('@s4/2 abc/2', 'TTAA', '+', 'PPPP'),
                    ('@s5/2 abc/2', 'AACC', '+', 'PPPP'),
                    ('@s6/2 abc/2', 'AAAA', '+', 'PPPP'),
                    ('@s7/2 abc/2', 'CGGC', '+', 'PPPP'),
                    ('@s8/2 abc/2', 'GGAA', '+', 'PPPP'),
                    ('@s9/2 abc/2', 'CGGC', '+', 'PPPP'),
                    ('@s10/2 abc/2', 'CGGC', '+', 'PPPP'),
                    ('@s11/2 abc/2', 'GGAA', '+', 'PPPP')]

        golaybarcodes = [  # ATGATGCGACCA -> ACGATGCGACCA
                         ('@s1/2 abc/2', 'ATGATGCGACCA', '+', 'YYYYYYYYYYYY'),
                         ('@s2/2 abc/2', 'AGCTATCCACGA', '+', 'PPPPPPPPPPPP'),
                         ('@s3/2 abc/2', 'ACACACTATGGC', '+', 'PPPPPPPPPPPP'),
                         ('@s4/2 abc/2', 'AGCTATCCACGA', '+', 'PPPPPPPPPPPP'),
                         ('@s5/2 abc/2', 'ACACACTATGGC', '+', 'PPPPPPPPPPPP'),
                         ('@s6/2 abc/2', 'ACGATGCGACCA', '+', 'PPPPPPPPPPPP'),
                         # CATTGTATCAAC -> CATCGTATCAAC
                         ('@s7/2 abc/2', 'CATTGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s8/2 abc/2', 'CTAACGCAGGGG', '+', 'PPPPPPPPPPPP'),
                         ('@s9/2 abc/2', 'CATCGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s10/2 abc/2', 'CATCGTATCAAC', '+', 'PPPPPPPPPPPP'),
                         ('@s11/2 abc/2', 'CTAACGCAGTCA', '+', 'PPPPPPPPPPPP')]

        self.sequences = [('@s1/1 abc/1', 'GGG', '+', 'YYY'),
                          ('@s2/1 abc/1', 'CCC', '+', 'PPP'),
                          ('@s3/1 abc/1', 'AAA', '+', 'PPP'),
                          ('@s4/1 abc/1', 'TTT', '+', 'PPP'),
                          ('@s5/1 abc/1', 'ATA', '+', 'PPP'),
                          ('@s6/1 abc/1', 'TAT', '+', 'PPP'),
                          ('@s7/1 abc/1', 'CGC', '+', 'PPP'),
                          ('@s8/1 abc/1', 'GCG', '+', 'PPP'),
                          ('@s9/1 abc/1', 'ACG', '+', 'PPP'),
                          ('@s10/1 abc/1', 'GCA', '+', 'PPP'),
                          ('@s11/1 abc/1', 'TGA', '+', 'PPP')]
        self.bsi = BarcodeSequenceFastqIterator(barcodes, self.sequences)
        barcode_map = pd.Series(
            ['AAAA', 'AACC', 'TTAA', 'GGAA', 'CGGC'], name='bc',
            index=pd.Index(['sample1', 'sample2', 'sample3', 'sample4',
                            'sample5'], name='id')
        )
        self.barcode_map = qiime2.CategoricalMetadataColumn(barcode_map)

        self.bsi_werr = BarcodeSequenceFastqIterator(golaybarcodes,
                                                     self.sequences)

        golay_barcode_map = pd.Series(
            ['ACGATGCGACCA', 'ACACACTATGGC', 'AGCTATCCACGA',
             'CTAACGCAGTCA', 'CATCGTATCAAC'], name='bc',
            index=pd.Index(['sample1', 'sample2', 'sample3', 'sample4',
                            'sample5'], name='id')
        )
        self.golay_barcode_map = qiime2.CategoricalMetadataColumn(
            golay_barcode_map)

    def test_partition(self):
        demux, _ = emp_single(self.bsi, self.barcode_map,
                              golay_error_correction=False)

        partition = partition_samples_single(demux)

        exp_samples = ('sample1_1_L001_R1_001.fastq.gz',
                       'sample2_3_L001_R1_001.fastq.gz',
                       'sample3_2_L001_R1_001.fastq.gz',
                       'sample4_5_L001_R1_001.fastq.gz',
                       'sample5_4_L001_R1_001.fastq.gz')
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = ['sample-id,filename,direction\n',
                            f'sample{idx + 1},{exp_samples[idx]},forward\n']
            self._compare_manifests(act_manifest, exp_manifest)

            output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
            self.assertEqual(len(output_fastq), 1)

            self._validate_sample_fastq(
                output_fastq[0][1].open(), self.sequences, exp_indices[idx])

    def test_partition_num_specified(self):
        demux, _ = emp_single(self.bsi, self.barcode_map,
                              golay_error_correction=False)
        partition = partition_samples_single(demux, 2)
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

        sample = partition[1]
        act_manifest = list(sample.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample1,sample1_1_L001_R1_001.fastq.gz,forward\n',
                        'sample2,sample2_3_L001_R1_001.fastq.gz,forward\n',
                        'sample3,sample3_2_L001_R1_001.fastq.gz,forward\n']
        self._compare_manifests(act_manifest, exp_manifest)

        output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
        self.assertEqual(len(output_fastq), 3)

        self._validate_sample_fastq(
            output_fastq[0][1].open(), self.sequences, exp_indices[0])
        self._validate_sample_fastq(
            output_fastq[1][1].open(), self.sequences, exp_indices[1])
        self._validate_sample_fastq(
            output_fastq[2][1].open(), self.sequences, exp_indices[2])

        sample = partition[2]
        act_manifest = list(sample.manifest.view(FastqManifestFormat).open())

        exp_manifest = ['sample-id,filename,direction\n',
                        'sample4,sample4_5_L001_R1_001.fastq.gz,forward\n',
                        'sample5,sample5_4_L001_R1_001.fastq.gz,forward\n']
        self._compare_manifests(act_manifest, exp_manifest)

        output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
        self.assertEqual(len(output_fastq), 2)

        self._validate_sample_fastq(
            output_fastq[0][1].open(), self.sequences, exp_indices[3])
        self._validate_sample_fastq(
            output_fastq[1][1].open(), self.sequences, exp_indices[4])

    def test_partition_more_partitions_than_samples(self):
        demux, _ = emp_single(self.bsi, self.barcode_map,
                              golay_error_correction=False)

        with self.assertWarnsRegex(
                UserWarning, "You have requested a number of.*100.*5.*5"):
            partition = partition_samples_single(demux, 100)

        exp_samples = ('sample1_1_L001_R1_001.fastq.gz',
                       'sample2_3_L001_R1_001.fastq.gz',
                       'sample3_2_L001_R1_001.fastq.gz',
                       'sample4_5_L001_R1_001.fastq.gz',
                       'sample5_4_L001_R1_001.fastq.gz')
        exp_indices = ([0, 5], [2, 4], [1, 3], [7, 10], [6, 8, 9])

        for idx, (id, sample) in enumerate(partition.items()):
            self.assertEqual(id, f'sample{idx + 1}')

            act_manifest = \
                list(sample.manifest.view(FastqManifestFormat).open())
            exp_manifest = ['sample-id,filename,direction\n',
                            f'sample{idx + 1},{exp_samples[idx]},forward\n']
            self._compare_manifests(act_manifest, exp_manifest)

            output_fastq = list(sample.sequences.iter_views(FastqGzFormat))
            self.assertEqual(len(output_fastq), 1)

            self._validate_sample_fastq(
                output_fastq[0][1].open(), self.sequences, exp_indices[idx])
