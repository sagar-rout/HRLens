# HR System Data Model Documentation

## Overview
This document describes the data model for the HR system, which manages employee information, departments, salary details, leave records, and branch information.

## Data Structure

### Employee (Root Document)

#### employee_id
- Type: keyword
- Description: Unique identifier for each employee
- Format: EMP-YYYYMMDD-XXXX (e.g., EMP-20240315-0001)

### Personal Information (personal_info)
- **first_name**: 
  - Type: text with keyword sub-field
  - Description: Employee's first name
  - Search: Full-text and exact matching
- **last_name**: 
  - Type: text with keyword sub-field
  - Description: Employee's last name
  - Search: Full-text and exact matching
- **email**: 
  - Type: keyword
  - Description: Corporate email address
- **phone**: 
  - Type: keyword
  - Description: Contact number
- **date_of_birth**: 
  - Type: date
  - Description: Date of birth (YYYY-MM-DD)
- **gender**: 
  - Type: keyword
  - Description: Gender (Male/Female/Other)
- **marital_status**: 
  - Type: keyword
  - Description: Marital status (Single/Married/Divorced/Widowed)

### Employment Details (employment_details)
- **hire_date**: 
  - Type: date
  - Description: Date when employee joined (YYYY-MM-DD)
- **position**: 
  - Type: keyword
  - Description: Current job position
- **department**: 
  - Type: object
  - Properties:
    - id: keyword
    - name: keyword
  - Description: Department information
- **manager_id**: 
  - Type: keyword
  - Description: Reference to supervisor's employee_id
- **employment_status**: 
  - Type: keyword
  - Description: Current status (Active/Inactive/On Leave/Terminated)
- **employment_type**: 
  - Type: keyword
  - Description: Type of employment (Full-time/Part-time/Contract)

### Salary Information (salary_info)
- **base_salary**: 
  - Type: float
  - Description: Current base salary amount
- **currency**: 
  - Type: keyword
  - Description: Salary currency code (USD/EUR/GBP etc.)
- **salary_history**: 
  - Type: nested
  - Properties:
    - effective_date: date
    - amount: float
    - reason: keyword
  - Description: Array of historical salary records

### Leave Records (leave_records)
- Type: nested
- Properties:
  - **leave_id**: 
    - Type: keyword
    - Description: Unique identifier for leave request
  - **leave_type**: 
    - Type: keyword
    - Description: Type of leave
  - **start_date**: 
    - Type: date
    - Description: Leave start date
  - **end_date**: 
    - Type: date
    - Description: Leave end date
  - **status**: 
    - Type: keyword
    - Description: Leave status
  - **reason**: 
    - Type: text
    - Description: Description of leave reason

### Address
- **street**: 
  - Type: text
  - Description: Street address
- **city**: 
  - Type: keyword
  - Description: City name
- **state**: 
  - Type: keyword
  - Description: State/Province
- **country**: 
  - Type: keyword
  - Description: Country name
- **postal_code**: 
  - Type: keyword
  - Description: Postal/ZIP code

### Branch
- **branch_id**: 
  - Type: keyword
  - Description: Unique identifier for branch
- **branch_name**: 
  - Type: keyword
  - Description: Name of the branch
- **location**: 
  - Type: geo_point
  - Description: Geographical coordinates (latitude, longitude)

### Metadata
- **created_at**: 
  - Type: date
  - Description: Record creation timestamp
- **updated_at**: 
  - Type: date
  - Description: Last update timestamp

## Query Patterns

### 1. Text Search
```json
{
  "multi_match": {
    "query": "search_term",
    "fields": ["personal_info.first_name", "personal_info.last_name"]
  }
}
```

### 2. Date Range
```json
{
  "range": {
    "employment_details.hire_date": {
      "gte": "start_date",
      "lte": "end_date"
    }
  }
}
```

### 3. Nested Queries
```json
{
  "nested": {
    "path": "leave_records",
    "query": {
      "bool": {
        "must": [
          {"term": {"leave_records.status": "Approved"}}
        ]
      }
    }
  }
}
```

### 4. Geo Queries
```json
{
  "geo_distance": {
    "distance": "10km",
    "branch.location": {
      "lat": latitude,
      "lon": longitude
    }
  }
}
```

## Query Guidelines

### Field Type Usage
- Use `term`/`terms` for keyword fields (exact matching)
- Use `match`/`multi_match` for text fields (full-text search)
- Use `range` for dates and numbers
- Use `nested` for salary_history and leave_records
- Use `geo_distance` for location-based queries

### Common HR Query Patterns
1. Employee Search:
   - Name search (text/keyword)
   - ID lookup (keyword)
   - Department filtering (keyword)
   - Status filtering (keyword)

2. Salary Analysis:
   - Range queries
   - Historical changes
   - Department averages

3. Leave Management:
   - Current leave status
   - Leave history
   - Leave type distribution

4. Geographical:
   - Branch location queries
   - Employee distribution
   - Regional analysis

### Performance Optimization
1. Use keyword fields for:
   - Exact matching
   - Sorting
   - Aggregations

2. Use text fields for:
   - Full-text search
   - Partial matching
   - Name searches

3. Nested Query Considerations:
   - Use sparingly
   - Consider performance impact
   - Limit nested query depth

4. Geo Queries:
   - Include reasonable distance bounds
   - Use appropriate precision level
   - Consider caching for frequent queries

## Example Queries

### 1. Find employees in Engineering
```json
{
  "term": {
    "employment_details.department.name": "Engineering"
  }
}
```

### 2. Recent Hires
```json
{
  "range": {
    "employment_details.hire_date": {
      "gte": "now-6M"
    }
  }
}
```

### 3. Active Leave Status
```json
{
  "nested": {
    "path": "leave_records",
    "query": {
      "bool": {
        "must": [
          {"term": {"leave_records.status": "Approved"}},
          {"range": {"leave_records.end_date": {"gte": "now"}}}
        ]
      }
    }
  }
}
```

## Usage Guidelines
1. Always use UTC for all datetime fields
2. Maintain referential integrity for manager_id references
3. Ensure all monetary values are stored in the smallest currency unit
4. Use ISO country codes for country fields
5. Follow the specified ID formats for various identifiers 