# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (needed for Render)
EXPOSE 3000

# Start the Slack bot
CMD ["python", "slack_main.py"]
