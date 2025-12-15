FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for database
RUN mkdir -p instance

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
