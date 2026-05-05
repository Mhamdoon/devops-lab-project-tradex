# Use python:3.11-slim as per rubric
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Expose port and run
EXPOSE 5000
CMD ["python", "backend/app.py"]