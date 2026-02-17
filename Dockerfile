# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/src/frontend
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY src/backend/ ./src/backend/

# Copy frontend build from stage 1
COPY --from=frontend-build /app/src/frontend/dist ./src/frontend/dist

# Copy synthetic test data (needed for demo pre-loading)
COPY data/synthetic-faxes/ ./data/synthetic-faxes/

# Create data directories for runtime
RUN mkdir -p ./data/uploads

# Railway sets PORT env var
ENV PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn src.backend.main:app --host 0.0.0.0 --port ${PORT}"]
