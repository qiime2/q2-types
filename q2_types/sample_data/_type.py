# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import AlphaDiversityDirectoryFormat


SampleData = SemanticType('SampleData', field_names='type')

AlphaDiversity = SemanticType('AlphaDiversity',
                              variant_of=SampleData.field['type'])

plugin.register_semantic_types(SampleData, AlphaDiversity)

plugin.register_artifact_class(
    SampleData[AlphaDiversity],
    directory_format=AlphaDiversityDirectoryFormat,
    description=("Alpha diversity values, each associated with a single "
                 "sample identifier.")
)
