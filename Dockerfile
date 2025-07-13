# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 (if any) and other tools
# apt-get update and apt-get install are for Debian/Ubuntu based images
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    # Add any other system-level dependencies required by ultralytics (YOLO) if known.
    # Often, Python packages handle most of their C/C++ dependencies.
    # For YOLO, you might need specific CUDA/GPU drivers if you plan to use GPU,
    # but for CPU-only, these typically aren't needed at this stage.
    # If ultralytics complains about missing shared libraries, add them here.
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port FastAPI will run on (e.g., 8000)
EXPOSE 8000

# Command to run the application (e.g., your Dagster webserver or FastAPI)
# This will be overridden by docker-compose for specific services,
# but provides a default for just running the Python app.
CMD ["python", "app_startup_script.py"] # Placeholder, will refine with Dagster