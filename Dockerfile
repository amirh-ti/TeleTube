FROM python:3.12-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        aria2 \
        curl \
        ca-certificates \
        unzip \
    && rm -rf /var/lib/apt/lists/*


RUN curl -fsSL https://deno.land/install.sh | sh
ENV PATH="/root/.deno/bin:${PATH}"
ENV DENO_INSTALL="/root/.deno"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN mkdir -p /app/data
ENV DOWNLOAD_DIR="/app/data/downloads"
ENV COOKIES_FILE="/app/data/cookies.txt"

# پورت وب‌سرور (لینک مستقیم + پنل مدیریت). Railway خودش از env var PORT
# استفاده می‌کنه؛ این EXPOSE فقط جنبه‌ی مستندسازیه.
EXPOSE 8080

CMD ["python3", "bot.py"]