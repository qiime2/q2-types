from rachis.plugin.testing import TestPluginBase


class TestExamples(TestPluginBase):
    package = 'q2_types.tests'

    def test_examples(self):
        self.execute_examples()
