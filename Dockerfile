FROM python:3.11-slim

# Install ffmpeg (required for yt-dlp) and build tools (required for shazamio-core / Rust)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Run bot
CMD ["python", "bot.py"]
