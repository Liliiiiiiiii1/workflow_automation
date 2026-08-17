# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency list and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Set timezone to Asia/Yerevan
ENV TZ=Asia/Yerevan

# Run the script when container starts
CMD ["python", "main.py"]
