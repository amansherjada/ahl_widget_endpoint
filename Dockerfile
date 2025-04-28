# Use Slim image instead of Alpine
FROM python:3.11-slim

# Install build tools and other essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    curl \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy your app code
COPY . .

# Expose Flask app port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
