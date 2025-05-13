# Use official Python image as the base
FROM python:3.11-slim

# Set environment variables to prevent bytecode creation and ensure logs are shown
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "fastapi_newqa:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
