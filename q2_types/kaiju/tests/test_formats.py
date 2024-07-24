# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
from qiime2.plugin.testing import TestPluginBase

from q2_types.kaiju import KaijuDBDirectoryFormat


class TestFormats(TestPluginBase):
    package = "q2_types.kaiju.tests"

    def test_kaiju_dirfmt(self):
        dirpath = self.get_data_path("db-valid")
        format = KaijuDBDirectoryFormat(dirpath, mode="r")
        format.validate()


if __name__ == "__main__":
    unittest.main()
