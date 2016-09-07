# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio

from ..plugin_setup import plugin
from ._format import LSMatFormat


@plugin.register_transformer
def _1(data: skbio.DistanceMatrix) -> LSMatFormat:
    ff = LSMatFormat()
    with ff.open() as fh:
        data.write(fh, format='lsmat')
    return ff


@plugin.register_transformer
def _2(ff: LSMatFormat) -> skbio.DistanceMatrix:
    return skbio.DistanceMatrix.read(str(ff), format='lsmat', verify=False)
