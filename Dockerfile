# syntax=docker/dockerfile:1

# Backend - Python
# Use the official Python image as the base image
FROM python:3.11

# Copy the backend directory contents into the container at /app
COPY . /app

# Set the working directory in the container to /app
WORKDIR /app

# Copy the environment file
COPY .env /app/.env

# Create a directory for static files
RUN mkdir -p /app/static

# Copy static files if they exist (using a wildcard to avoid errors if the directory is empty)
COPY static/* /app/static/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the app
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
