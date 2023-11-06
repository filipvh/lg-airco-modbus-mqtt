# Use the official Python 3.11 image as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install OS dependencies (if any), keeping the image as small as possible
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy the requirements.txt file into the container at /usr/src/app/
COPY requirements.txt .
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the codebase into the container
COPY version.info .
COPY ./src ./src

# Command to run the application
CMD ["python", "src/server.py"]
