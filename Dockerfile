# Use the official Python image as the base image
FROM python:3.12-slim


# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Expose port 5000 to the outside world
EXPOSE 8000

# Command to run the Python application
CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"]
