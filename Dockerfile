# Use official Python 3.12 image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# Install uv package manager (using pip with China mirror)
RUN pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir

# Copy project files
COPY pyproject.toml uv.lock ./
COPY main.py ./
COPY tools/ ./tools/

# Install dependencies
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1

# Run application
CMD ["uv", "run", "python", "main.py"]
