# HRLens

HRLens is an AI-powered HR analytics and search platform that enables natural language querying of HR data using LLMs, vector search, and Elasticsearch.

## Features

- Natural language query processing
- Vector-based semantic caching using Milvus
- Elasticsearch-based data storage and retrieval
- Performance tracking and monitoring

## Architecture

### Core Components

1. **Search Agent**: Converts natural language to Elasticsearch queries
2. **Vector Cache**: Stores semantically similar queries in Milvus
3. **Elasticsearch**: Primary data storage and search engine

### Query Processing Flow

```mermaid
graph TD
    A[User Query] --> B[Generate Query Vector]
    B --> C{Check Vector Cache}
    C -->|Cache Hit| D[Retrieve ES Query]
    C -->|Cache Miss| E[Generate ES Query via LLM]
    E --> F[Store in Vector Cache]
    D --> G[Execute ES Search]
    F --> G
    G --> H[Return Results]
```

1. **Query Processing**
   - Convert natural language query to vector embedding
   - Check Milvus for similar existing queries
   - Generate new ES query via LLM if needed

2. **Search Execution**
   - Use cached or newly generated Elasticsearch query
   - Execute search and return results
   - Cache new queries for future use

## Setup

### Prerequisites

- Python 3.9+
- Elasticsearch 8.x
- Milvus 2.x
- OpenAI API key

### Installation

1. Clone and setup environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment (.env):
```bash
OPENAI_API_KEY=your_api_key
ES_HOSTS=http://localhost:9200
ELASTICSEARCH_INDEX=hr_lens
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

3. Start services:
```bash
docker-compose up -d
```

4. Run application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Search
```http
POST /api/search
Content-Type: application/json

{
  "query": "Find engineers in India"
}
```

### Cache Statistics
```http
GET /api/cache/stats
```

### Clear Cache
```http
POST /api/clear_cache
```

## Dependencies

- FastAPI
- Elasticsearch
- OpenAI
- LangChain
- Milvus
- Pydantic

For detailed configuration options, see `app/config.py`.