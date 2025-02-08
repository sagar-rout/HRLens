import sys
from loguru import logger
from app.utils.path_utils import get_project_root

# Remove default logger
logger.remove()

# Create logs directory
log_path = get_project_root() / "logs"
log_path.mkdir(exist_ok=True)

# Simple format for all logs
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Console handler
logger.add(
    sys.stdout,
    format=log_format,
    level="INFO",
    colorize=True
)

# File handler for all logs
logger.add(
    log_path / "app.log",
    format=log_format,
    level="DEBUG",
    rotation="1 day",
    retention="7 days"
)

# File handler for errors
logger.add(
    log_path / "error.log",
    format=log_format,
    level="ERROR",
    rotation="1 day",
    retention="7 days"
)
