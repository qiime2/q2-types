# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

__version__ = "0.0.7.dev0"  # noqa

# TODO remove all imports and from __all__ because they are available as public
# imports in their respective subpackages. These imports are here so the
# existing tests will pass; they can be removed when the tests are rewritten.

from .feature_table import (FeatureTable, Frequency, RelativeFrequency,
                            PresenceAbsence)
from .distance_matrix import DistanceMatrix
from .sample_data import SampleData, AlphaDiversity
from .tree import Phylogeny, Rooted, Unrooted
from .ordination import PCoAResults
from .feature_data import (FeatureData, Taxonomy, Sequence, PairedEndSequence,
                           AlignedSequence, DNAIterator, PairedDNAIterator)
from .reference_features import ReferenceFeatures, SSU
from .per_sample_sequences import (SequencesWithQuality,
                                   PairedEndSequencesWithQuality)

__all__ = ['DistanceMatrix', 'Phylogeny', 'PCoAResults', 'FeatureTable',
           'Frequency', 'RelativeFrequency', 'PresenceAbsence',
           'SampleData', 'AlphaDiversity', 'FeatureData', 'Taxonomy',
           'Sequence', 'PairedEndSequence', 'AlignedSequence',
           'ReferenceFeatures', 'SSU', 'Rooted', 'Unrooted', 'DNAIterator',
           'PairedDNAIterator', 'SequencesWithQuality',
           'PairedEndSequencesWithQuality']
