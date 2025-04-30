# Start from a lightweight Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy your Python script
COPY caption_image.py .

# Copy your example images folder
COPY images/ images/

# Install required Python packages
RUN pip install --no-cache-dir requests pandas

# Set the default command to run your script
CMD ["python", "caption_image.py"]
