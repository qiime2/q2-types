# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_data_mag._deferred_setup._validators import (
    ALLOWED_SEPARATORS,
    _check_pooled_contig_ids,
)
from q2_types.per_sample_sequences import ContigSequencesDirFmt


class TestPooledContigValidator(TestPluginBase):
    package = "q2_types.feature_data_mag.tests"

    def _get_contigs(self, case):
        return ContigSequencesDirFmt(
            self.get_data_path(f"pooled-contigs/{case}"), mode="r"
        )

    def _assert_validation_error(self, case, error_message):
        with self.assertRaises(ValidationError) as context:
            _check_pooled_contig_ids(self._get_contigs(case), "max")
        self.assertEqual(str(context.exception), error_message)

    def test_valid(self):
        _check_pooled_contig_ids(self._get_contigs("valid"), "max")

    def test_unsupported_separator(self):
        allowed = ", ".join(repr(sep) for sep in ALLOWED_SEPARATORS)
        self._assert_validation_error(
            "unsupported-separator",
            'Contig ID "sample1-dPj72SpWBxMXAVyPtYqJGA" uses the separator '
            f'"-", which is not supported. Allowed separators are: {allowed}.',
        )

    def test_bare_uuid(self):
        self._assert_validation_error(
            "bare-uuid",
            'Contig ID "0196f161-8053-5ff2-827b-6c454fc3c449" is not of the '
            'form "<sample-id><separator><uuid or shortuuid>".',
        )

    def test_empty_prefix(self):
        self._assert_validation_error(
            "empty-prefix",
            'Contig ID "_0196f161-8053-5ff2-827b-6c454fc3c449" is not of the '
            'form "<sample-id><separator><uuid or shortuuid>".',
        )

    def test_no_suffix(self):
        self._assert_validation_error(
            "no-suffix",
            'Contig ID "contig_1" is not of the form '
            '"<sample-id><separator><uuid or shortuuid>".',
        )

    def test_mixed_separators(self):
        self._assert_validation_error(
            "mixed-separators",
            'Contig ID "sample2_2Ta5AWdPGsJiCUZJ4NeP9A" uses the separator '
            '"_", expected ":".',
        )

    def test_multiple_files(self):
        self._assert_validation_error(
            "two-files",
            "Pooled contigs must be stored in a single FASTA file; found 2.",
        )


if __name__ == "__main__":
    unittest.main()
