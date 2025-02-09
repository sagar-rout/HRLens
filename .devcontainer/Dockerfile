FROM python:3.9-slim

# Install essential packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python packages for development
RUN pip install --no-cache-dir \
    pylint \
    black \
    pytest \
    pytest-cov

# Keep container running
CMD ["sleep", "infinity"]
