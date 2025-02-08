import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional

class LoggerSetup:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance

    @staticmethod
    def _setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_format)
            
            # File handler with rotation
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                f"{log_dir}/app.log",
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            file_handler.setFormatter(file_format)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

# Create a default logger instance
logger = LoggerSetup.get_logger()
