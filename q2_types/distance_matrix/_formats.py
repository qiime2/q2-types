# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
from skbio.io import FileFormatError
from skbio.stats.distance import PairwiseMatrixError


class LSMatFormat(model.TextFileFormat):
    """An lsmat distance matrix with non-empty square float data, unique IDs,
    symmetric values, and a zero-valued diagonal.
    """
    def _validate_(self, level):
        try:
            skbio.DistanceMatrix.read(str(self), format='lsmat')
        except (FileFormatError, PairwiseMatrixError, ValueError) as error:
            raise ValidationError(error) from error


DistanceMatrixDirectoryFormat = model.SingleFileDirectoryFormat(
    'DistanceMatrixDirectoryFormat', 'distance-matrix.tsv', LSMatFormat)
