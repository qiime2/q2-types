# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pkg_resources
import tempfile
import unittest


# TODO port this to qiime.core.testing.base. Split out into more specific
# subclasses if necessary.
class TestPluginBase(unittest.TestCase):
    # TODO raise better error message if subclasses forget to override
    # (__new__ or ABC?)
    package = None

    def setUp(self):
        # TODO generalize plugin lookup when ported to framework. Perhaps test
        # that the plugin is registered, which would be a stronger test than
        # simply importing.
        try:
            from q2_types.plugin_setup import plugin
        except ImportError:
            self.fail("Could not import plugin object.")

        self.plugin = plugin

        # TODO use qiime temp dir when ported to framework, and when the
        # configurable temp dir exists
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix='q2-types-test-temp-')

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_data_path(self, filename):
        return pkg_resources.resource_filename(self.package,
                                               'data/%s' % filename)

    def get_transformer(self, from_type, to_type):
        try:
            transformer_record = self.plugin.transformers[from_type, to_type]
        except KeyError:
            self.fail(
                "Could not find registered transformer from %r to %r." %
                (from_type, to_type))

        return transformer_record.transformer
