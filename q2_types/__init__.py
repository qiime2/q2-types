# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

__version__ = "0.0.2"  # noqa

from .feature_table import (FeatureTable, Frequency, RelativeFrequency,
                            PresenceAbsence)
from .distance_matrix import DistanceMatrix
from ._sample_data import SampleData, AlphaDiversity
from ._tree import Phylogeny, Rooted, Unrooted
from .ordination import PCoAResults
from ._feature_data import (FeatureData, Taxonomy, Sequence, PairedEndSequence,
                            AlignedSequence, DNAIterator, PairedDNAIterator)
from ._reference_features import ReferenceFeatures, SSU
from ._per_sample_sequences import (SequencesWithQuality,
                                    PairedEndSequencesWithQuality)

__all__ = ['DistanceMatrix', 'Phylogeny', 'PCoAResults', 'FeatureTable',
           'Frequency', 'RelativeFrequency', 'PresenceAbsence',
           'SampleData', 'AlphaDiversity', 'FeatureData', 'Taxonomy',
           'Sequence', 'PairedEndSequence', 'AlignedSequence',
           'ReferenceFeatures', 'SSU', 'Rooted', 'Unrooted', 'DNAIterator',
           'PairedDNAIterator', 'SequencesWithQuality',
           'PairedEndSequencesWithQuality']
