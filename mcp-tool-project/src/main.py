def main():
    from mcp_tool.sdk_interface import SDKInterface
    from mcp_tool.test_suite import TestSuite

    # Initialize the SDK
    sdk = SDKInterface()
    sdk.initialize_sdk()

    # Run the test suite
    test_suite = TestSuite()
    test_suite.run_tests()

    # Fetch and print the results
    results = test_suite.get_results()
    print("Test Results:", results)


if __name__ == "__main__":
    main()