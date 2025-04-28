# Correct base image (NO ALPINE, NO 3.13)
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    curl \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port Flask uses
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
