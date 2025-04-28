# Use a secure, lightweight Python 3.13 Alpine base
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (Alpine package names are different)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy application files
COPY app.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for mounted secrets
RUN mkdir -p /secrets

# Set environment variables
ENV PORT 8080

# Expose port 8080
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
