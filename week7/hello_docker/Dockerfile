# Start from a small Python base image
FROM python:3.12-slim

# Set metadata
LABEL maintainer="Walid Sati"
LABEL description="Hello from Docker"

# Set working directory inside the container
WORKDIR /app

# Copy the script
COPY hello.py .

# Environment variable (can be overridden at runtime)
ENV APP_ENV=development

# What to run when the container starts
CMD ["python", "hello.py"]

