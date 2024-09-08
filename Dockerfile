# syntax=docker/dockerfile:1

# Use the official Python image as the base image
FROM python:3.11

# Set environment variables to optimize image
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the git_api directory and its contents into the container at /app/git_api
RUN mkdir -p /app/github_api
COPY github_api/* /app/git_api/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for static files
RUN mkdir -p /app/static

# Copy static files if they exist (using a wildcard to avoid errors if the directory is empty)
COPY static/* /app/static/

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]