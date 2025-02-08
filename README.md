# HRLens

An intelligent HR search system using semantic caching and vector similarity.

## Overview

HRLens is a natural language search interface for HR data that combines:
- Semantic understanding using LLMs
- Vector similarity caching
- Elasticsearch for data storage and retrieval
- Milvus for vector similarity search

## Features

- Natural language query processing
- Semantic query caching
- Vector similarity matching
- Intelligent query transformation
- Performance metrics tracking
- Cache statistics monitoring

## Architecture

### Core Components

1. **Search Agent**
   - Converts natural language to Elasticsearch queries
   - Uses OpenAI embeddings for semantic understanding
   - Manages query caching and retrieval

2. **Vector Cache**
   - Stores semantically similar queries
   - Uses Milvus for vector similarity search
   - Implements intelligent cache matching

3. **Cache Stats**
   - Tracks cache performance metrics
   - Monitors hit/miss rates
   - Stores statistics in Elasticsearch

4. **Service Container**
   - Manages dependency injection
   - Handles service lifecycle
   - Ensures singleton instances

### Project Structure

```
HRLens/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── search.py         # API endpoints
│   ├── core/
│   │   ├── container.py         # Dependency injection
│   │   ├── services.py          # Service interfaces
│   │   ├── search_agent.py      # Query processing
│   │   ├── vector_cache.py      # Cache management
│   │   ├── cache_stats.py       # Statistics tracking
│   │   └── elasticsearch_client.py
│   ├── schema/
│   │   ├── templates/           # Query templates
│   │   └── docs/               # System documentation
│   └── utils/
│       └── logger.py           # Logging utilities
├── tests/
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

### 1. Search API
```http
POST /api/search
Content-Type: application/json

{
    "query": "find all software engineers"
}
```

Response:
```json
{
    "results": {
        "hits": {
            "total": {"value": 50},
            "hits": [...]
        }
    },
    "metrics": {
        "cache_hit": true,
        "search_time": 0.123
    }
}
```

### 2. Cache Statistics
```http
GET /api/cache/stats
```

Response:
```json
{
    "status": "success",
    "data": {
        "performance": {
            "total_queries": 100,
            "hits": 75,
            "misses": 25,
            "hit_rate": "75.0%"
        },
        "cache": {
            "total_entries": 50,
            "queries_cached": 50
        },
        "last_activity": {
            "last_hit": {
                "query": "find engineers",
                "time": "2024-02-08T12:34:56"
            },
            "last_miss": {
                "query": "new query",
                "time": "2024-02-08T12:35:00"
            }
        }
    }
}
```

## Setup

1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Start Services
```bash
docker-compose up -d
```

3. Run Application
```bash
uvicorn app.main:app --reload
```

## Configuration

Key configuration options in `.env`:
```env
OPENAI_API_KEY=your_api_key
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_INDEX=hr_lens
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Dependencies

- Python 3.9+
- FastAPI
- Elasticsearch
- Milvus
- OpenAI
- LangChain