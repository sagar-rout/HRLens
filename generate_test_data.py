from datetime import datetime, timedelta
import random
import json
from faker import Faker
from elasticsearch import Elasticsearch
import uuid
from app.config import get_settings
from app.utils.path_utils import get_schema_path

# Initialize Faker and settings
fake = Faker()
settings = get_settings()

# Constants
DEPARTMENTS = [
    {"id": "DEP-001", "name": "Engineering"},
    {"id": "DEP-002", "name": "Human Resources"},
    {"id": "DEP-003", "name": "Finance"},
    {"id": "DEP-004", "name": "Marketing"},
    {"id": "DEP-005", "name": "Sales"},
    {"id": "DEP-006", "name": "Operations"},
    {"id": "DEP-007", "name": "Legal"},
    {"id": "DEP-008", "name": "Research & Development"},
]

POSITIONS = [
    "Software Engineer",
    "HR Manager",
    "Financial Analyst",
    "Marketing Specialist",
    "Sales Representative",
    "Operations Manager",
    "Legal Counsel",
    "Research Scientist",
]

EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract", "Intern", "Consultant"]
EMPLOYMENT_STATUS = ["Active", "Inactive", "On Leave", "Terminated"]
LEAVE_TYPES = [
    "Annual Leave",
    "Sick Leave",
    "Maternity Leave",
    "Paternity Leave",
    "Unpaid Leave",
]
LEAVE_STATUS = ["Pending", "Approved", "Rejected", "Cancelled"]


def generate_employee_id():
    return f"EMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4]}"


def generate_salary_history(base_salary):
    history = []
    date = datetime.now() - timedelta(days=random.randint(365, 1095))

    for _ in range(random.randint(1, 4)):
        history.append(
            {
                "effective_date": date.strftime("%Y-%m-%d"),
                "amount": base_salary * (0.8 + random.random() * 0.4),
                "reason": random.choice(
                    ["Promotion", "Annual Review", "Market Adjustment"]
                ),
            }
        )
        date += timedelta(days=random.randint(180, 365))

    return history


def generate_leave_records():
    records = []
    for _ in range(random.randint(0, 5)):
        start_date = datetime.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(days=random.randint(1, 14))
        records.append(
            {
                "leave_id": f"LEAVE-{uuid.uuid4().hex[:8]}",
                "leave_type": random.choice(LEAVE_TYPES),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": random.choice(LEAVE_STATUS),
                "reason": fake.sentence(),
            }
        )
    return records


def generate_employee():
    department = random.choice(DEPARTMENTS)
    base_salary = random.randint(30000, 150000)
    hire_date = fake.date_between(start_date="-10y", end_date="today")

    return {
        "employee_id": generate_employee_id(),
        "personal_info": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "date_of_birth": fake.date_of_birth(
                minimum_age=20, maximum_age=65
            ).strftime("%Y-%m-%d"),
            "gender": random.choice(["Male", "Female", "Other"]),
            "marital_status": random.choice(
                ["Single", "Married", "Divorced", "Widowed"]
            ),
        },
        "employment_details": {
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "position": random.choice(POSITIONS),
            "department": department,
            "manager_id": generate_employee_id(),
            "employment_status": random.choice(EMPLOYMENT_STATUS),
            "employment_type": random.choice(EMPLOYMENT_TYPES),
        },
        "salary_info": {
            "base_salary": base_salary,
            "currency": "USD",
            "salary_history": generate_salary_history(base_salary),
        },
        "leave_records": generate_leave_records(),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "country": fake.country(),
            "postal_code": fake.postcode(),
        },
        "branch": {
            "branch_id": f"BR-{fake.random_int(min=100, max=999)}",
            "branch_name": f"{fake.city()} Branch",
            "location": {"lat": float(fake.latitude()), "lon": float(fake.longitude())},
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def main():
    # Initialize Elasticsearch client
    es = Elasticsearch(settings.elasticsearch_host)

    # Get schema path and read mapping file
    schema_path = get_schema_path()
    with open(schema_path / "elasticsearch" / "mapping.json", "r") as f:
        mapping = json.load(f)

    # Create index with mapping
    if es.indices.exists(index=settings.elasticsearch_index):
        es.indices.delete(index=settings.elasticsearch_index)

    es.indices.create(index=settings.elasticsearch_index, body=mapping)

    # Generate and index employees
    for _ in range(1000):
        employee = generate_employee()
        es.index(index=settings.elasticsearch_index, document=employee)

    print(
        f"Successfully generated and indexed 1000 employee records in index: {settings.elasticsearch_index}"
    )


if __name__ == "__main__":
    main()
