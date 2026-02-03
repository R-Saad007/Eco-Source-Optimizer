# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# FIX: Copy requirements.txt from the 'backend' folder on the host
# Because context is '.', we must specify the path 'backend/requirements.txt'
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend folder into /app/backend
# This recreates your folder structure inside the container
COPY backend/ ./backend/

# Expose the port
EXPOSE 8000

# Run uvicorn pointing to the module "backend.server"
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]