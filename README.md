# HRLens

HRLens is an intelligent HR search system that converts natural language queries into Elasticsearch queries, making it easy to search and analyze HR data. It uses OpenAI's GPT models to understand natural language questions and generates precise Elasticsearch queries.

## Features

- Natural language to Elasticsearch query conversion
- Support for complex search patterns and aggregations
- Real-time query generation using OpenAI's GPT models
- FastAPI-based REST API with async operations
- Structured logging with Loguru
- Bruno HTTP client for API testing and documentation
- Comprehensive HR data model with nested fields

## Setup Guide

### Prerequisites

- Python 3.10+
- Elasticsearch 8.x
- OpenAI API key
- Bruno (for API testing)

### 1. Setup Elasticsearch

1. Start Elasticsearch:
```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.1
```

2. Verify Elasticsearch is running:
```bash
curl http://localhost:9200
```

### 2. Setup Application

1. Clone and setup environment:
```bash
git clone https://github.com/yourusername/HRLens.git
cd HRLens
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_INDEX=hr_data
```

3. Generate and load test data:
```bash
python generate_test_data.py
```

This creates sample:
- Employee records with realistic data
- Department structures
- Salary information
- Performance reviews
- Leave records

4. Start the application:
```bash
uvicorn app.main:app --reload
```

### 3. Setup Bruno for Testing

1. Install Bruno from [https://www.usebruno.com/](https://www.usebruno.com/)
2. Open Bruno and load the `http/hrlens` collection
3. Run the example queries

## Usage Examples

### API Endpoints

POST /api/v1/search/
```json
// Request
{
  "query": "find all engineers"
}

// Response
{
  "query": {
    "query": {
      "match": {
        "employment_details.job_title": "engineer"
      }
    }
  },
  "results": {
    "hits": {
      "total": {"value": 50},
      "hits": [...]
    }
  }
}
```

### Example Queries

1. Basic Search:
```
"find all software engineers"
"show me employees in the HR department"
```

2. Aggregations:
```
"how many employees do we have in each department"
"what is the average salary by department"
```

3. Complex Queries:
```
"find engineers with salary above 100000"
"show employees hired in the last 6 months"
```

## Project Structure
```
HRLens/
├── app/
│   ├── api/v1/search.py      # API endpoints
│   ├── core/                 # Core business logic
│   ├── schema/               # Templates and docs
│   └── utils/                # Utilities
├── http/                     # Bruno API tests
│   └── hrlens/
│       ├── search.bru
│       └── environment.bru
├── tests/
├── .env
└── requirements.txt
```