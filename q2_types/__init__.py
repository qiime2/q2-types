# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

__version__ = "0.0.1"  # noqa

from ._feature_table import (FeatureTable, Frequency, RelativeFrequency,
                             PresenceAbsence)
from ._distance_matrix import DistanceMatrix
from ._alpha_diversity import AlphaDiversity
from ._tree import Phylogeny
from ._ordination import PCoAResults

__all__ = ['DistanceMatrix', 'Phylogeny', 'PCoAResults', 'FeatureTable',
           'Frequency', 'RelativeFrequency', 'PresenceAbsence',
           'AlphaDiversity']
