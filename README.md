# PromoSearch MCP Server

A Model Context Protocol (MCP) server that provides semantic search, promotional ad optimization, and query understanding capabilities for AI agents.

## 🚀 Features

The PromoSearch MCP Server provides 4 composable tools for AI agents:

### 🔍 Core Tools

1. **expand_query** - Query expansion using LLM to generate long-tail keywords
2. **search_promotions** - Semantic search over promotion index using embeddings
3. **rank_promotions** - Rank promotions based on CTR/CVR prediction and user profiles
4. **optimize_ad_slots** - Optimize ad insertion positions in search results

### 🎯 Key Capabilities

- **Semantic Recall**: Understand natural language queries and retrieve relevant promotions
- **Intelligent Ranking**: CTR/CVR prediction with user profile personalization
- **Slot Optimization**: Context-aware ad placement with optimal insertion positions
- **Query Understanding**: Expand short queries into comprehensive long-tail keywords

## 📁 Project Structure

```
promosearch-mcp-server/
├── mcp_server/                     # Main MCP Server package
│   ├── __init__.py
│   ├── main.py                     # FastMCP entry point
│   ├── tools/                      # MCP tool implementations
│   │   ├── expand_query.py
│   │   ├── search_promotions.py
│   │   ├── rank_promotions.py
│   │   └── optimize_ad_slots.py
│   └── schemas/                    # JSON schemas (auto-generated)
├── models/                         # ML models and utilities
│   ├── embedder.py                # Sentence transformers for semantic search
│   └── ranker.py                  # CTR/CVR ranking models
├── data/                          # Data and indices
│   └── promotions.jsonl          # Promotion database
├── agents/                        # Demo and testing
│   └── demo_agent.py             # Usage examples
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd promosearch-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Install the package**
   ```bash
   pip install -e .
   ```

## ⚙️ Configuration

Create a `.env` file with the following configuration:

```env
# LLM API Keys (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration
DEFAULT_LLM_PROVIDER=openai  # or anthropic
EMBEDDING_MODEL=all-MiniLM-L6-v2
RANKING_MODEL_TYPE=mock  # or lightgbm

# Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO

# Data Configuration
PROMOTIONS_DATA_PATH=data/promotions.jsonl
EMBEDDINGS_CACHE_PATH=data/embeddings/
MAX_SEARCH_RESULTS=20
MAX_EXPANDED_QUERIES=5
```

## 🚀 Usage

### Starting the MCP Server

```bash
# Using the installed script
promosearch-server

# Or directly with Python
python -m mcp_server.main
```

### Running the Demo

```bash
python agents/demo_agent.py
```

### intergration with Cline
in the config of Cline add:
```bash
{
  "mcpServers": {
    "promosearch": {
      "command": "python",
      "args": ["/Users/guyunpei/Downloads/PromoSearchMCP/mcp_server/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key",
        "DEFAULT_LLM_PROVIDER": "openai",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```


### MCP Tool Usage

#### 1. Query Expansion

```python
# Expand a natural language query
result = await mcp_client.call_tool("expand_query", {
    "query": "我想找最近 AWS 云主机有哪些优惠"
})
# Returns: {"expanded_queries": ["aws ec2 discount", "cloud hosting deals", ...]}
```

#### 2. Semantic Search

```python
# Search for relevant promotions
result = await mcp_client.call_tool("search_promotions", {
    "query": "cloud hosting services",
    "user_profile": {
        "user_type": "professional",
        "interests": ["cloud", "hosting", "aws"],
        "budget_level": "medium"
    }
})
# Returns: {"results": [{"id": "...", "title": "...", "score": 0.85}, ...]}
```

#### 3. Promotion Ranking

```python
# Rank promotion candidates
result = await mcp_client.call_tool("rank_promotions", {
    "candidates": promotion_list,
    "user_profile": user_profile
})
# Returns: {"ranked_promotions": [{"id": "...", "score": 0.92}, ...]}
```

#### 4. Ad Slot Optimization

```python
# Optimize ad placement in search results
result = await mcp_client.call_tool("optimize_ad_slots", {
    "search_results": search_result_list,
    "promotions": top_promotions
})
# Returns: {"injected_results": [...]}
```

### Complete Pipeline Example

```python
# 1. Expand query
expanded = await call_tool("expand_query", {"query": user_query})

# 2. Search promotions for each expanded query
all_promotions = []
for query in expanded["expanded_queries"]:
    results = await call_tool("search_promotions", {
        "query": query, 
        "user_profile": user_profile
    })
    all_promotions.extend(results["results"])

# 3. Rank promotions
ranked = await call_tool("rank_promotions", {
    "candidates": all_promotions,
    "user_profile": user_profile
})

# 4. Optimize ad slots
final_results = await call_tool("optimize_ad_slots", {
    "search_results": organic_results,
    "promotions": ranked["ranked_promotions"][:3]
})
```

## 🧪 Technical Implementation

### Semantic Search
- Uses `sentence-transformers` with `all-MiniLM-L6-v2` model
- Cosine similarity for matching
- User profile boosting for personalization
- Efficient vector caching

### Ranking Model
- LightGBM for CTR/CVR prediction (with mock fallback)
- Feature engineering from user profiles and promotion metadata
- Budget compatibility scoring
- Interest matching algorithms

### Query Expansion
- LLM-powered expansion (OpenAI/Anthropic)
- Rule-based fallback for reliability
- Category-specific expansion strategies
- Promotional term injection

### Ad Slot Optimization
- Rule-based insertion strategy
- Context-aware positioning
- Contextual ad copy generation
- User experience preservation

## 📊 Performance

- **Tool Response Time**: < 500ms per tool call
- **Semantic Search**: Supports 10K+ promotions with sub-second search
- **Concurrent Requests**: Handles multiple simultaneous MCP calls
- **Memory Usage**: Efficient embedding caching and model loading

## 🧩 MCP Integration

This server implements the Model Context Protocol specification and can be used with any MCP-compatible client:

- **Claude Desktop**: Add to MCP configuration
- **Custom Agents**: Use MCP client libraries
- **Development Tools**: Integrate with IDEs and workflows

### MCP Configuration Example

```json
{
  "mcpServers": {
    "promosearch": {
      "command": "promosearch-server",
      "args": [],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

## 🔧 Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black mcp_server/ models/ agents/
isort mcp_server/ models/ agents/
```

### Adding New Promotions

Add entries to `data/promotions.jsonl`:

```json
{"id": "new-promo", "title": "New Promotion", "description": "...", "categories": ["..."], "price_tier": "medium", "base_ctr": 0.1}
```

### Extending Tools

1. Create new tool in `mcp_server/tools/`
2. Register in `mcp_server/main.py`
3. Add to demo script for testing

## 📈 Roadmap

- [ ] Advanced ranking models (neural networks)
- [ ] Real-time promotion updates
- [ ] A/B testing framework
- [ ] Analytics and metrics collection
- [ ] Multi-language support
- [ ] Advanced user profiling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: See `/docs` folder
- **Examples**: Check `/agents/demo_agent.py`

---

Built with ❤️ for the MCP ecosystem
