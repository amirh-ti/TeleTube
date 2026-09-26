"""
تنظیمات runtime که از پنل مدیریت قابل تغییرن، بدون نیاز به ری‌استارت یا
ری‌دیپلوی. توی یک فایل JSON ساده ذخیره می‌شن (نیازی به دیتابیس نیست).

این جدا از config.py هست: config.py مقادیر ثابتی هستن که فقط از env خونده
می‌شن (نیاز به ری‌استارت دارن)، ولی این‌ها toggleهایی هستن که ادمین می‌خواد
سریع از پنل عوضشون کنه.
"""
import json
import os
import threading

from config import SETTINGS_PATH

_DEFAULTS = {
    "enable_direct_links": True,
    "enable_channel_delivery": True,
    "enable_nimbaha": False,
    "enable_urldl": False,
}

_lock = threading.Lock()


def _load():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(_DEFAULTS)
            merged.update(data)
            return merged
        except Exception:
            pass
    return dict(_DEFAULTS)


def get_settings():
    with _lock:
        return _load()


def update_settings(new_values: dict):
    """new_values فقط کلیدهایی که می‌خوای تغییر بدن رو داشته باشه."""
    with _lock:
        current = _load()
        current.update(new_values)
        os.makedirs(os.path.dirname(SETTINGS_PATH) or ".", exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        return current
