FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt to the working directory in the container
COPY requirements.txt /app/

# Install dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into the container
COPY . /app/

# Expose port 8080
EXPOSE 8080

# Run the Flask application
CMD ["python", "app.py"]
