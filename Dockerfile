FROM python:3.12-slim

# ffmpeg برای merge صدا/تصویر، aria2 برای دانلود موازی سریع، curl برای نصب Deno
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        aria2 \
        curl \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Deno برای حل چالش‌های جاوااسکریپتی یوتیوب (nsig)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV PATH="/root/.deno/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# فایل‌های کوکی و دانلود موقت باید به‌عنوان volume به کانتینر متصل بشن، مثلا:
#   docker run -v /root/cookies.txt:/root/cookies.txt -v ytbot-data:/root/youtube_memory ...
CMD ["python3", "bot.py"]
