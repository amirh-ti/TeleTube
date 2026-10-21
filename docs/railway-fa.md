
### راهنمای استقرار گام‌به‌گام

1. **فورک کردن مخزن (Repository)**
به [مخزن گیت‌هاب TeleTube](https://github.com/amirh-ti/TeleTube) بروید و روی دکمه **Fork** کلیک کنید تا یک کپی از آن تحت حساب گیت‌هاب خودتان ایجاد شود.
2. **ایجاد یک پروژه جدید در Railway**
* وارد حساب کاربری خود در [Railway](https://railway.com) شوید.
* روی گزینه **New Project** و سپس **Deploy from GitHub repo** کلیک کنید.
* مخزن فورک‌شده TeleTube را از فهرست انتخاب کنید.


3. **پیکربندی متغیرهای محیطی (Environment Variables)**
پلتفرم Railway به‌طور خودکار سرویس را تشخیص داده و از شما می‌خواهد که متغیرها را اضافه کنید. برای این کار می‌توانید از یکی از دو روش زیر استفاده کنید:
* **روش اول: افزودن تک‌به‌تک متغیرها**
به تب **Variables** بروید، روی **New Variable** کلیک کنید و هر متغیر را به همراه نام و مقدار آن به‌صورت جداگانه اضافه نمایید.
* **روش دوم: استفاده از Raw Editor**
روی دکمه **Raw Editor** در همان تب کلیک کنید و تمامی متغیرهای خود را به‌صورت یکجا و با قالب زیر در آنجا قرار دهید:


```env
API_HASH="a5a6ab85da5*****ae1731"
API_ID="299***22"
COOKIES_B64="IyBOZXRz******IyBUaGlzIGlzIGEgZ2VuZXJhdGVkIGZILEggRG8gbm90IGVkaXQugoKLnlvdXR1YmUuY29tCVRSVUUJLwlUUlV*****Q3NzYyMQlfX1NlY3VyZS1ST0xMT1VUX1RP*********nTVlwc2FveHRqOWxnTSUzRAo="
SESSION_STRING="1BJWap1sBuxJgoGdFww01wyaSMnq9G9tBGyhVZWzuEnY**********gW8JdbuVdR_QfAmDCEQ="
TARGET_CHANNEL="https://t.me/YourChannelID"
TARGET_CHANNEL_USERNAME="@YourChannelID"
TELEGRAM_TOKEN="88****33:AAGDRhUo******gKfTpYSvF0k"
ADMIN_CHAT_ID="7827********781"
ADMIN_PANEL_PASSWORD="YourPass"
LINK_TTL_HOURS="24"
PUBLIC_BASE_URL="https://YourPublicBaseUrl"

```

4. دوباره Deploy کنید و اذت ببرید !

---
