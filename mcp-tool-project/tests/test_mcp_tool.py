import unittest
from mcp_tool.sdk_interface import SDKInterface
from mcp_tool.test_suite import TestSuite

class TestMCPTool(unittest.TestCase):

    def setUp(self):
        self.sdk_interface = SDKInterface()
        self.test_suite = TestSuite()

    def test_initialize_sdk(self):
        result = self.sdk_interface.initialize_sdk()
        self.assertTrue(result)

    def test_fetch_data(self):
        self.sdk_interface.initialize_sdk()
        data = self.sdk_interface.fetch_data()
        self.assertIsNotNone(data)

    def test_run_tests(self):
        results = self.test_suite.run_tests()
        self.assertIsInstance(results, dict)

    def test_get_results(self):
        self.test_suite.run_tests()
        results = self.test_suite.get_results()
        self.assertIn('passed', results)
        self.assertIn('failed', results)

if __name__ == '__main__':
    unittest.main()