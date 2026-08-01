"""
🔐 Telegram Session String Generator / تولیدکننده رشته سشن تلگرام
Generates a Telegram session string for use with Telethon.
تولید رشته سشن تلگرام برای استفاده با Telethon.
"""

import os
import asyncio
from telethon.sessions import StringSession
from telethon.sync import TelegramClient


async def main():
    """
    Main function / تابع اصلی
    Generates and saves session string / تولید و ذخیره رشته سشن
    """
    print("=" * 50)
    print("🔐 Telegram Session String Generator / تولیدکننده رشته سشن تلگرام")
    print("=" * 50)
    print()
    
    # --- Get credentials from user / دریافت اطلاعات از کاربر ---
    try:
        api_id = int(input("📱 Enter API ID / وارد کنید API ID: ").strip())
    except ValueError:
        print("❌ Error / خطا: API ID must be a number / باید عدد باشد!")
        return

    api_hash = input("🔑 Enter API Hash / وارد کنید API Hash: ").strip()

    if not api_id or not api_hash:
        print("❌ Error / خطا: API ID and API Hash cannot be empty / نمی‌توانند خالی باشند!")
        return

    print("\n📡 Connecting to Telegram / در حال اتصال به تلگرام...")
    
    # --- Create Telegram client / ساخت کلاینت تلگرام ---
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        # --- Get session string / دریافت رشته سشن ---
        session_string = client.session.save()
        
        # --- File path / مسیر فایل ---
        file_path = "/root/sess.txt"
        
        try:
            # --- Create directory if not exists / ایجاد پوشه در صورت عدم وجود ---
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # --- Save to file / ذخیره در فایل ---
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(session_string)
                
            print("\n" + "=" * 50)
            print("✅ Success! / موفق!")
            print("=" * 50)
            print(f"📁 Session String saved to / ذخیره شد در: {file_path}")
            print("\n📋 Your Session String / رشته سشن شما:")
            print("-" * 50)
            print(session_string)
            print("-" * 50)
            print("\n💡 Keep this string safe! It gives access to your account.")
            print("💡 این رشته را امن نگه دارید! به حساب شما دسترسی می‌دهد.")
            
        except PermissionError:
            print(f"\n❌ Permission Error / خطای دسترسی: Cannot write to / نمی‌توان در {file_path} نوشت. Try running with 'sudo' / با 'sudo' اجرا کنید.")
        except Exception as e:
            print(f"\n❌ Failed to save file / ذخیره فایل ناموفق: {e}")


if __name__ == "__main__":
    asyncio.run(main())
