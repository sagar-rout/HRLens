from pathlib import Path

def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent

def get_app_path() -> Path:
    """Returns app folder path."""
    return get_project_root() / "app"

def get_schema_path() -> Path:
    """Returns schema folder path."""
    return get_app_path() / "schema" 