# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio

from ..plugin_setup import plugin
from . import OrdinationFormat


@plugin.register_transformer
def _1(data: skbio.OrdinationResults) -> OrdinationFormat:
    ff = OrdinationFormat()
    data.write(str(ff), format='ordination')
    return ff


@plugin.register_transformer
def _2(ff: OrdinationFormat) -> skbio.OrdinationResults:
    return skbio.OrdinationResults.read(str(ff), format='ordination',
                                        verify=False)
