# CDP Agentkit Extension - Langchain Toolkit
CDP integration with Langchain to enable agentic workflows using the core primitives defined in `cdp-agentkit-core`.

This toolkit contains tools that enable an LLM agent to interact with the [Coinbase Developer Platform](https://docs.cdp.coinbase.com/). The toolkit provides a wrapper around the CDP SDK, allowing agents to perform onchain operations like transfers, trades, and smart contract interactions.

## Setup

### Prerequisites
- Python 3.10 or higher 
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)

### Installation

```bash
pip install cdp-langchain
```

### Environment Setup

Set the following environment variables:

```bash
export CDP_API_KEY_NAME=<your-api-key-name>
export CDP_API_KEY_PRIVATE_KEY=$'<your-private-key>'
export NETWORK_ID=base-sepolia  # Optional: Defaults to base-sepolia

# LLM Configuration (choose one provider)
# Option 1: OpenAI
export OPENAI_API_KEY=<your-openai-api-key>

# Option 2: OpenRouter
export OPENROUTER_API_KEY=<your-openrouter-api-key>
export OPENROUTER_BASE_URL=https://openrouter.ai/api/v1  # Optional: Defaults to OpenRouter API
export MODEL_NAME=gpt-4  # Optional: Defaults to gpt-4
```

## Usage

### Basic Setup

```python
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Initialize CDP wrapper
cdp = CdpAgentkitWrapper()

# Create toolkit from wrapper
toolkit = CdpToolkit.from_cdp_agentkit_wrapper(cdp)
```

View available tools:
```python
tools = toolkit.get_tools()
for tool in tools:
    print(tool.name)
```

The toolkit provides the following tools:

1. **get_wallet_details** - Get details about the MPC Wallet
2. **get_balance** - Get balance for specific assets
3. **request_faucet_funds** - Request test tokens from faucet
4. **transfer** - Transfer assets between addresses
5. **trade** - Trade assets (Mainnet only)
6. **deploy_token** - Deploy ERC-20 token contracts
7. **mint_nft** - Mint NFTs from existing contracts
8. **deploy_nft** - Deploy new NFT contracts
9. **register_basename** - Register a basename for the wallet

### Using with an Agent

The toolkit supports multiple LLM providers through the CdpAgentkitWrapper's configuration. The wrapper will automatically use OpenRouter if configured, otherwise falling back to OpenAI.

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Initialize CDP wrapper with LLM configuration
cdp = CdpAgentkitWrapper()

# Get tools and create agent
tools = toolkit.get_tools()

# The wrapper automatically configures the LLM based on your environment
llm = cdp.get_llm()
agent_executor = create_react_agent(llm, tools)

# Example usage
events = agent_executor.stream(
    {"messages": [("user", "Send 0.005 ETH to john2879.base.eth")]},
    stream_mode="values"
)

for event in events:
    event["messages"][-1].pretty_print()
```
Expected output:
```
Transferred 0.005 of eth to john2879.base.eth.
Transaction hash for the transfer: 0x78c7c2878659a0de216d0764fc87eff0d38b47f3315fa02ba493a83d8e782d1e
Transaction link for the transfer: https://sepolia.basescan.org/tx/0x78c7c2878659a0de216d0764fc87eff0d38b47f3315fa02ba493a83d8e782d1
```
## LLM Configuration

The toolkit supports two LLM providers:
1. **OpenAI** (default) - Requires `OPENAI_API_KEY`
2. **OpenRouter** - Requires `OPENROUTER_API_KEY`, with optional `OPENROUTER_BASE_URL` and `MODEL_NAME`

The CdpAgentkitWrapper will automatically use OpenRouter if `OPENROUTER_API_KEY` is set, otherwise falling back to OpenAI configuration.

## CDP Tookit Specific Features

### Wallet Management
The toolkit maintains an MPC wallet that persists between sessions:

```python
# Export wallet data
wallet_data = cdp.export_wallet()

# Import wallet data
values = {"cdp_wallet_data": wallet_data}
cdp = CdpAgentkitWrapper(**values)
```

### Network Support
The toolkit supports [multiple networks](https://docs.cdp.coinbase.com/cdp-sdk/docs/networks).

### Gasless Transactions
The following operations support gasless transactions on Base Mainnet:
- USDC transfers
- EURC transfers
- cbBTC transfers

## Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed setup instructions and contribution guidelines.

## Documentation
For detailed documentation of all CDP features and configurations, visit:
- [CDP Documentation](https://docs.cdp.coinbase.com/mpc-wallet/docs/welcome)
- [API Reference](https://api.python.langchain.com/en/latest/agent_toolkits/cdp_langchain.agent_toolkits.cdp_toolkit.CDPToolkit.html)
