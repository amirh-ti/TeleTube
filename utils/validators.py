"""اعتبارسنجی ورودی‌های کاربر."""
import re

YOUTUBE_URL_RE = re.compile(r"https?://(www\.)?(youtube\.com|youtu\.be)/")


def is_valid_youtube_url(url):
    return bool(YOUTUBE_URL_RE.match(url.strip()))
