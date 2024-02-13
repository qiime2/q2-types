# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import model
from q2_types.reference_db._format import (
    NCBITaxonomyNamesFormat, NCBITaxonomyNodesFormat
)
from ..plugin_setup import plugin


class KaijuIndexFormat(model.BinaryFileFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _validate_(self, level):
        pass


class KaijuDBDirectoryFormat(model.DirectoryFormat):
    nodes = model.File(r"nodes.dmp", format=NCBITaxonomyNodesFormat)
    names = model.File(r"names.dmp", format=NCBITaxonomyNamesFormat)
    index = model.File(r"kaiju_db.+\.fmi", format=KaijuIndexFormat)


plugin.register_formats(KaijuDBDirectoryFormat)
