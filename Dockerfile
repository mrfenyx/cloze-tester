FROM python:3.13-slim

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose port (Flask defaults to 5000)
EXPOSE 5000

# Entrypoint
CMD ["python", "app.py"]
