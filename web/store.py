"""
مدیریت متادیتای لینک‌های مستقیم دانلود (توکن، فایل، زمان انقضا، تعداد
دانلود). روی یک فایل JSON ساده ذخیره می‌شه — برای این مقیاس نیازی به
دیتابیس واقعی نیست.
"""
import json
import os
import time
import uuid
import threading

from config import LINKS_DB_PATH, LINK_TTL_HOURS
from utils.logger import logger

_lock = threading.Lock()


def _load():
    if os.path.exists(LINKS_DB_PATH):
        try:
            with open(LINKS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save(data):
    os.makedirs(os.path.dirname(LINKS_DB_PATH) or ".", exist_ok=True)
    with open(LINKS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_link(file_path, title, size_bytes, ttl_hours=None):
    """یک توکن یکتا برای فایل می‌سازه و متادیتاش رو ذخیره می‌کنه."""
    ttl_hours = ttl_hours or LINK_TTL_HOURS
    token = uuid.uuid4().hex
    now = time.time()
    entry = {
        "token": token,
        "file_path": file_path,
        "title": title,
        "size_bytes": size_bytes,
        "created_at": now,
        "expires_at": now + ttl_hours * 3600,
        "downloads": 0,
    }
    with _lock:
        data = _load()
        data[token] = entry
        _save(data)
    return entry


def get_link(token):
    """اگه لینک وجود داشته و منقضی نشده باشه، متادیتاش رو برمی‌گردونه."""
    with _lock:
        data = _load()
    entry = data.get(token)
    if not entry:
        return None
    if entry["expires_at"] < time.time():
        return None
    return entry


def record_download(token):
    with _lock:
        data = _load()
        if token in data:
            data[token]["downloads"] += 1
            _save(data)


def list_links(include_expired=False):
    with _lock:
        data = _load()
    now = time.time()
    items = list(data.values())
    if not include_expired:
        items = [i for i in items if i["expires_at"] >= now]
    items.sort(key=lambda i: i["created_at"], reverse=True)
    return items


def delete_link(token, delete_file=True):
    """فایل‌ها رو پاک می‌کنه اما رکورد رو با برچسب حذف‌شده توی دیتابیس نگه می‌داره."""
    with _lock:
        data = _load()
        entry = data.get(token)
        if entry:
            entry["is_deleted"] = True  # به جای حذف رکورد، فقط برچسب می‌زنیم
            _save(data)
            
    if entry and delete_file:
        p = entry.get("file_path")
        t = entry.get("thumb_path")
        try:
            if p and os.path.exists(p):
                os.remove(p)
            if t and os.path.exists(t):
                os.remove(t)
        except Exception as e:
            logger.error(f"خطا در حذف فایل‌های لینک {token}: {e}")
            
    return entry


def purge_expired():
    """فایل‌های منقضی‌شده رو پاک می‌کنه اما رکوردشون در داشبورد می‌مونه."""
    with _lock:
        data = _load()
        now = time.time()
        # پیدا کردن لینک‌هایی که منقضی شدن ولی هنوز برچسب حذف نخوردن
        expired_tokens = [t for t, e in data.items() if e["expires_at"] < now and not e.get("is_deleted")]
        removed = []
        for t in expired_tokens:
            data[t]["is_deleted"] = True
            removed.append(data[t])
            
        if expired_tokens:
            _save(data)
            
    for entry in removed:
        p = entry.get("file_path")
        t = entry.get("thumb_path")
        try:
            if p and os.path.exists(p):
                os.remove(p)
            if t and os.path.exists(t):
                os.remove(t)
            logger.info(f"فایل و تامبنیل لینک منقضی‌شده حذف شد: {p}")
        except Exception as e:
            logger.error(f"خطا در حذف فایل منقضی {p}: {e}")
            
    return removed


def update_link_extras(token, thumb_path=None, urldl_link=None, tg_link=None):
    """اطلاعات تکمیلی مثل تامبنیل و لینک‌های اضافه رو به دیتابیس متصل می‌کنه."""
    with _lock:
        data = _load()
        if token in data:
            data[token]["thumb_path"] = thumb_path
            data[token]["urldl_link"] = urldl_link
            data[token]["tg_link"] = tg_link
            _save(data)
