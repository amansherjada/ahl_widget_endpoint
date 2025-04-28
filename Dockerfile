FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (add full stack for numpy, wheels, etc)
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev py3-pip build-base lapack-dev libatlas-base-dev

# Copy application files
COPY app.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for mounted secrets
RUN mkdir -p /secrets

# Set environment variables
ENV PORT 8080

# Expose port 8080
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
