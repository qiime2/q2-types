# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
import skbio.io
from qiime.plugin import SemanticType, FileFormat, DataLayout

from .plugin_setup import plugin


PCoAResults = SemanticType('PCoAResults')


class OrdinationFormat(FileFormat):
    name = 'ordination'

    @classmethod
    def sniff(cls, filepath):
        sniffer = skbio.io.io_registry.get_sniffer('ordination')
        return sniffer(filepath)[0]

ordination_data_layout = DataLayout('ordination', 1)
ordination_data_layout.register_file('ordination.txt', OrdinationFormat)


def ordination_to_skbio_ordination_results(data_dir):
    with open(os.path.join(data_dir, 'ordination.txt'), 'r') as fh:
        return skbio.OrdinationResults.read(fh, format='ordination',
                                            verify=False)


def skbio_ordination_results_to_ordination(view, data_dir):
    with open(os.path.join(data_dir, 'ordination.txt'), 'w') as fh:
        view.write(fh, format='ordination')


plugin.register_data_layout(ordination_data_layout)

plugin.register_data_layout_reader('ordination', 1, skbio.OrdinationResults,
                                   ordination_to_skbio_ordination_results)

plugin.register_data_layout_writer('ordination', 1, skbio.OrdinationResults,
                                   skbio_ordination_results_to_ordination)

plugin.register_semantic_type(PCoAResults)

plugin.register_type_to_data_layout(PCoAResults, 'ordination', 1)
