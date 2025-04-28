# Use Python 3.11 Alpine as base image
FROM python:3.11-alpine

# Install build dependencies required for numpy and other packages
RUN apk add --no-cache gcc g++ musl-dev libffi-dev

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt first (for better caching)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
