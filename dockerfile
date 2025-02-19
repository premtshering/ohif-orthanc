FROM python:3.7

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy scripts
COPY ./scripts /scripts

# Set entry point
CMD ["python3", "/scripts/watch_import.py"]