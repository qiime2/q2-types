
# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from .. import (AlphaDiversityFormat, AlphaDiversityDirectoryFormat,
                SampleData, AlphaDiversity)

from ...plugin_setup import plugin


plugin.register_formats(AlphaDiversityFormat, AlphaDiversityDirectoryFormat)

plugin.register_semantic_types(SampleData, AlphaDiversity)

plugin.register_artifact_class(
    SampleData[AlphaDiversity],
    directory_format=AlphaDiversityDirectoryFormat,
    description=("Alpha diversity values, each associated with a single "
                 "sample identifier.")
)

importlib.import_module('._transformers', __name__)
