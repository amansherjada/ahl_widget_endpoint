FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ libffi-dev

# Copy app files
COPY app.py /app/
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /secrets

ENV PORT 8080
EXPOSE 8080

CMD ["python", "app.py"]
