# Stock Info Agent

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-000000)](https://fetch.ai/)

Real-time stock information agent built with Fetch.ai's uAgents framework. Provides stock market data retrieval with health monitoring and rate limiting.

## Features

- **Stock Data Retrieval** — Fetch real-time stock information via API
- **Chat Protocol** — Interactive chat-based queries for stock data
- **Structured Output** — Machine-readable responses for downstream agents
- **Health Monitoring** — Built-in health check protocol for agent status
- **Rate Limiting** — Request throttling via QuotaProtocol (60 req/hr)

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Fetch.ai uAgents |
| Rate Limiting | QuotaProtocol |
| Data Models | Pydantic |
| Protocol | Chat + Structured Output |

## Project Structure

```
stockagent/
└── stock_info_agent/
    ├── agent.py             # Main agent with protocol setup
    ├── client.py            # Client for testing agent queries
    ├── protocol.py          # Chat and structured output protocols
    └── stockinfoagent.py    # Stock data fetching logic
```

## Setup

```bash
cd stock_info_agent
pip install uagents
python agent.py
```

The agent starts on port 8005 with mailbox enabled and registers on Agentverse.

## Usage

Send stock queries via the chat protocol. The agent supports:

- Stock price lookups
- Market data retrieval
- Health status checks

## License

MIT
