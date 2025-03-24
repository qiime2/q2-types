# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import shutil

from q2_types.kraken2 import (
    Kraken2ReportDirectoryFormat,
    Kraken2OutputDirectoryFormat
)


def collate_kraken2_reports(kraken2_reports: Kraken2ReportDirectoryFormat) \
        -> Kraken2ReportDirectoryFormat:
    collated_kraken2_reports = Kraken2ReportDirectoryFormat()
    _collate_kraken_tsvs(kraken2_reports, 'report', collated_kraken2_reports)
    return collated_kraken2_reports


def collate_kraken2_outputs(kraken2_outputs: Kraken2OutputDirectoryFormat) \
        -> Kraken2OutputDirectoryFormat:
    collated_kraken2_outputs = Kraken2OutputDirectoryFormat()
    _collate_kraken_tsvs(kraken2_outputs, 'output', collated_kraken2_outputs)
    return collated_kraken2_outputs


def _collate_kraken_tsvs(kraken2_results, kraken_type, output):
    for kraken2_result in kraken2_results:
        for fp in kraken2_result.path.iterdir():
            shutil.move(str(fp), output.path / os.path.basename(fp))
