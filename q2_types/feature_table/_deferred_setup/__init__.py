# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

import biom

from qiime2.plugin import Citations

from .. import (BIOMV100Format, BIOMV210Format, BIOMV100DirFmt,
                BIOMV210DirFmt, FeatureTable, Frequency, RelativeFrequency,
                PresenceAbsence, Composition, Balance,
                PercentileNormalized, Design, Normalized)

from ...plugin_setup import plugin

citations = Citations.load('citations.bib', package='q2_types.feature_table')

plugin.register_views(BIOMV100Format, BIOMV210Format, BIOMV100DirFmt,
                      BIOMV210DirFmt, biom.Table,
                      citations=[citations['mcdonald2012biological']])

plugin.register_semantic_types(FeatureTable, Frequency, RelativeFrequency,
                               PresenceAbsence, Balance, Composition,
                               PercentileNormalized, Design, Normalized)

plugin.register_artifact_class(
    FeatureTable[Frequency],
    directory_format=BIOMV210DirFmt,
    description=("A feature table (e.g., samples by ASVs) where each value "
                 "in the matrix is a whole number greater than or equal to "
                 "0 representing the frequency or count of a feature in "
                 "the corresponding sample. These data should be raw "
                 "(not normalized) counts.")
)
plugin.register_artifact_class(
    FeatureTable[RelativeFrequency],
    directory_format=BIOMV210DirFmt,
    description=("A feature table (e.g., samples by ASVs) where each value "
                 "in the matrix is a real number greater than or equal to "
                 "0.0 and less than or equal to 1.0 representing the "
                 "proportion of the sample that is composed of that feature. "
                 "The feature values for each sample should sum to 1.0.")
)
plugin.register_artifact_class(
    FeatureTable[PresenceAbsence],
    directory_format=BIOMV210DirFmt,
    description=("A feature table (e.g., samples by ASVs) where each value "
                 "indicates is a boolean indication of whether the feature "
                 "is observed in the sample or not.")
)
plugin.register_artifact_class(
    FeatureTable[Balance],
    directory_format=BIOMV210DirFmt
)
plugin.register_artifact_class(
    FeatureTable[Composition],
    directory_format=BIOMV210DirFmt,
    description=("A feature table (e.g., samples by ASVs) where each value "
                 "in the matrix is a whole number greater than "
                 "0 representing the frequency or count of a feature in "
                 "the corresponding sample. These data are typically not "
                 "raw counts, having been transformed in some way to exclude "
                 "zero counts.")
)
plugin.register_artifact_class(
    FeatureTable[PercentileNormalized],
    directory_format=BIOMV210DirFmt
)
plugin.register_artifact_class(
    FeatureTable[Design],
    directory_format=BIOMV210DirFmt
)
plugin.register_artifact_class(
    FeatureTable[Normalized],
    directory_format=BIOMV210DirFmt,
    description="A feature table that was normalized."
)

importlib.import_module('._transformers', __name__)
