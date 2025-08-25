# First Aid Assistant – Dockerfile
FROM python:3.11-slim

# System deps: ffmpeg for pydub conversions
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (assumes you will mount/bind or copy all .py files next to this Dockerfile)
COPY . /app

# Runtime env (override at docker run)
ENV GROQ_API_KEY=""
ENV ELEVENLABS_API_KEY=""

EXPOSE 7860

# Start the app
CMD ["python","app.py"]
