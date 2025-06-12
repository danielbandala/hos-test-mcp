class SDKInterface:
    def __init__(self):
        self.sdk_initialized = False

    def initialize_sdk(self):
        # Code to initialize the MCP SDK
        self.sdk_initialized = True
        return "SDK initialized"

    def fetch_data(self):
        if not self.sdk_initialized:
            raise Exception("SDK not initialized. Please initialize the SDK first.")
        # Code to fetch data from the MCP SDK
        return "Data fetched from SDK"