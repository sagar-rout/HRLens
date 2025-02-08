# HRLens

An intelligent HR search system using semantic caching and vector similarity.

## Overview

HRLens is a natural language search interface for HR data that combines:
- Semantic understanding using LLMs
- Intelligent in-memory caching with vector similarity
- Elasticsearch for data storage and retrieval
- Performance tracking and monitoring

## Features

- Natural language query processing
- Dual-layer caching system:
  - Exact string matching
  - Vector similarity matching
- Intelligent query transformation
- Performance metrics tracking
- Cache statistics monitoring

## Architecture

### Core Components

1. **Search Agent**
   - Converts natural language to Elasticsearch queries
   - Uses OpenAI embeddings for semantic understanding
   - Implements LRU caching with vector similarity
   - Manages both exact and semantic query matching

2. **Cache Stats**
   - Tracks cache performance metrics
   - Monitors hit/miss rates
   - Stores statistics in Elasticsearch

3. **Elasticsearch Client**
   - Handles search operations
   - Manages index operations
   - Provides robust error handling

### Project Structure

```
HRLens/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── search.py         # API endpoints
│   ├── core/
│   │   ├── search_agent.py      # Query processing & caching
│   │   ├── cache_stats.py       # Statistics tracking
│   │   └── elasticsearch_client.py
│   ├── schema/
│   │   └── templates/           # Query templates
│   └── utils/
│       └── logger.py           # Logging utilities
├── tests/
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

### 1. Search API
```http
POST /api/v1/search
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
GET /api/v1/cache/stats
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

## Caching System

The service implements a sophisticated dual-layer caching system:

1. **Exact Match Cache**
   - LRU (Least Recently Used) eviction policy
   - Direct string matching for identical queries
   - O(1) lookup time

2. **Semantic Match Cache**
   - Vector similarity comparison
   - Configurable similarity threshold (default: 0.95)
   - Catches semantically equivalent queries
   - Uses OpenAI embeddings for comparison

Features:
- Configurable cache size (default: 1000 entries)
- Automatic cache cleanup
- Performance metrics tracking
- Thread-safe operations

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
# API Settings
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# OpenAI Settings
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4-mini

# Elasticsearch Settings
ES_HOSTS=http://localhost:9200
ES_VERIFY_CERTS=true
ELASTICSEARCH_INDEX=hr_lens
```

## Dependencies

- Python 3.9+
- FastAPI
- Elasticsearch
- OpenAI
- LangChain
- NumPy (for vector operations)