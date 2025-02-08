# HRLens

HRLens is an intelligent HR search system that converts natural language queries into Elasticsearch queries, making it easy to search and analyze HR data.

## Features

- Natural language to Elasticsearch query conversion
- Support for complex search patterns and aggregations
- Real-time query generation using OpenAI's GPT models
- FastAPI-based REST API
- Async operations for better performance

## Prerequisites

- Python 3.10+
- Elasticsearch 8.x
- OpenAI API key
- Docker (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HRLens.git
cd HRLens
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_INDEX=hr_data
```

## Usage

1. Start the application:
```bash
uvicorn app.main:app --reload
```

2. Access the API at `http://localhost:8000`

3. Example API calls:

```bash
# Search for employees
curl -X POST "http://localhost:8000/api/v1/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "find all engineers in the software department"}'

# Count employees by department
curl -X POST "http://localhost:8000/api/v1/search/" \
     -H "Content-Type: application/json" \
     -d '{"query": "how many employees do we have in each department"}'
```

## API Endpoints

### POST /api/v1/search/
Converts natural language queries to Elasticsearch queries and returns results.

Request:
```json
{
  "query": "find all engineers"
}
```

Response:
```json
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

## Query Examples

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

## Development

### Project Structure
```
HRLens/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── search.py
│   ├── core/
│   │   ├── elasticsearch_client.py
│   │   ├── search_agent.py
│   │   └── factory.py
│   ├── schema/
│   │   ├── templates/
│   │   │   └── hr_system_template.py
│   │   └── docs/
│   │       └── DOCUMENT.md
│   ├── utils/
│   │   ├── logger.py
│   │   └── path_utils.py
│   └── main.py
├── tests/
├── .env
└── requirements.txt
```

### Generating Test Data

Use the provided script to generate test data:
```bash
python generate_test_data.py
```