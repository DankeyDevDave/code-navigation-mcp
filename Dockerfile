FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Create workspace directory for code analysis
RUN mkdir -p /workspace

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_MODE=server
ENV LOG_LEVEL=INFO

# Expose port for MCP server (if needed for future HTTP mode)
EXPOSE 8080

# Default command runs the server
CMD ["python", "server.py"]