# Use an official slim Python image (not Alpine, not Python 3.13)
FROM python:3.11-slim

# Set environment variables to avoid Python buffering issues
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    curl \
    && apt-get clean

# Set working directory inside container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy entire project files
COPY . .

# Expose the port Flask uses
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
