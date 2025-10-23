# Multi-stage build for ELCA Mothership AIs on Render
FROM python:3.11-slim as backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .
COPY enhanced_interactive_demo.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/health || exit 1

# Start command
CMD ["gunicorn", "enhanced_interactive_demo:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]

# Frontend stage
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend code
COPY frontend/ .

# Build the application
RUN npm run build

# Serve static files
FROM nginx:alpine
COPY --from=frontend /app/frontend/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]