from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    {
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
            "transport": "stdio"
        }
    }
)

