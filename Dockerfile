FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/raw data/processed models

# Set environment variables
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 5000

# Health check (use provided PORT if set)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/ || exit 1

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "web_app:app"]
