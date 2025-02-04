# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType


SampleData = SemanticType('SampleData', field_names='type')

AlphaDiversity = SemanticType('AlphaDiversity',
                              variant_of=SampleData.field['type'])
