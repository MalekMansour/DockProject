FROM python:3.9-slim

WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy requirements.txt to the working directory in the container
COPY requirements.txt .

# Install dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

EXPOSE 8080

# Set environment variable for Flask (optional)
ENV FLASK_APP=app.py

# Run the Flask application
CMD ["python", "app.py"]
