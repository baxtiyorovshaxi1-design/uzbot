FROM python:3.11-slim

# Install ffmpeg, nodejs (required by yt-dlp for YouTube JS extraction)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Always install the latest yt-dlp (YouTube/Instagram change APIs frequently)
RUN pip install --no-cache-dir --upgrade yt-dlp

# Copy bot files
COPY . .

# Run bot
CMD ["python", "bot.py"]
