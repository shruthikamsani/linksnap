# Start with an official Python image
FROM python:3.11-slim

# Set the working folder inside the container
WORKDIR /app

# Copy requirements list first
COPY requirements.txt .

# Install all packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your code
COPY . .

# Make sure templates folder exists
RUN mkdir -p templates

# The app runs on port 5000
EXPOSE 5000

# Start the app when container runs
CMD ["python", "app.py"]