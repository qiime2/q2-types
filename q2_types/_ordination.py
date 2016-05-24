# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
from qiime.plugin import SemanticType

from .plugin_setup import plugin


PCoAResults = SemanticType('PCoAResults')


def validator(data_dir):
    raise NotImplementedError()


def ordination_to_skbio_ordination_results(data_dir):
    with open(os.path.join(data_dir, 'ordination.txt'), 'r') as fh:
        return skbio.OrdinationResults.read(fh, format='ordination',
                                            verify=False)


def skbio_ordination_results_to_ordination(view, data_dir):
    with open(os.path.join(data_dir, 'ordination.txt'), 'w') as fh:
        view.write(fh, format='ordination')


plugin.register_archive_format('ordination', 1, validator)

plugin.register_archive_format_reader('ordination', 1,
                                      skbio.OrdinationResults,
                                      ordination_to_skbio_ordination_results)

plugin.register_archive_format_writer('ordination', 1,
                                      skbio.OrdinationResults,
                                      skbio_ordination_results_to_ordination)

plugin.register_semantic_type(PCoAResults)

plugin.register_type_to_archive_format(PCoAResults, 'ordination', 1)
