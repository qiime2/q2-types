# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import skbio

from q2_types.multiplexed_sequences import (
    MultiplexedFastaQualDirFmt, MultiplexedSingleEndBarcodeInSequenceDirFmt
)

from qiime2.plugin.testing import TestPluginBase


class TestMultiplexedSequencesTransformers(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def test_fasta_qual_to_fastq(self):
        _, obs = self.transform_format(
            MultiplexedFastaQualDirFmt,
            target=MultiplexedSingleEndBarcodeInSequenceDirFmt,
            filenames=('reads.fasta', 'reads.qual'))

        # TODO: can I access the file name (forward.fastq.gz) from result
        # so I'm not duplicating that here?
        sequences = skbio.io.read('%s/forward.fastq.gz' % str(obs),
                                  format='fastq',
                                  variant='illumina1.8')
        sequences = list(sequences)

        self.assertEqual(len(sequences), 3)

        self.assertTrue(str(sequences[0]).startswith('ACAGAGTCGGCTCA'))
        self.assertTrue(str(sequences[0]).endswith('ATGGGCTAGG'))
        self.assertTrue(str(sequences[1]).startswith('ACAGAGTCGGCTCA'))
        self.assertTrue(str(sequences[1]).endswith('CCGGTCGCCA'))
        self.assertTrue(str(sequences[2]).startswith('AGCACGAGCCTACA'))
        self.assertTrue(str(sequences[2]).endswith('GTCTCTTGGG'))

        self.assertEqual(sequences[0].metadata['id'], 'FLP3FBN01ELBSX')
        self.assertEqual(sequences[1].metadata['id'], 'FLP3FBN01EG8AX')
        self.assertEqual(sequences[2].metadata['id'], 'FLP3FBN01EEWKD')

        self.assertEqual(
            list(sequences[0].positional_metadata['quality'][:5]),
            [37, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[0].positional_metadata['quality'][-5:]),
            [21, 15, 15, 13, 13])
        self.assertEqual(
            list(sequences[1].positional_metadata['quality'][:5]),
            [37, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[1].positional_metadata['quality'][-5:]),
            [25, 25, 25, 25, 28])
        self.assertEqual(
            list(sequences[2].positional_metadata['quality'][:5]),
            [36, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[2].positional_metadata['quality'][-5:]),
            [36, 36, 36, 36, 36])
