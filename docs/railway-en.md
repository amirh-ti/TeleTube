### Step-by-Step Deployment

1. **Fork the Repository**
Head over to the [TeleTube GitHub repository](https://github.com/amirh-ti/TeleTube) and click the **Fork** button to create a copy under your own GitHub account.
2. **Create a New Project on Railway**
* Log in to [Railway](https://railway.com).
* Click **New Project** → **Deploy from GitHub repo**.
* Select your forked TeleTube repository from the list.


3. **Configure Environment Variables**
Railway will automatically detect the service and prompt you to add variables. You can add them using either of the two methods below:
* **Method 1: Adding variables one by one**
Go to the **Variables** tab, click **New Variable**, and add each variable individually with its corresponding name and value.
* **Method 2: Using the Raw Editor**
Click the **Raw Editor** button in the same tab and paste all your variables at once using the format below:


```env
API_HASH="a5a6ab85da5*****ae1731"
API_ID="299***22"
COOKIES_B64="IyBOZXRz******IyBUaGlzIGlzIGEgZ2VuZXJhdGVkIGZpbGUhIERvIG5vdCBlZGl0LgoKLnlvdXR1YmUuY29tCVRSVUUJLwlUUlV*****Q3NzYyMQlfX1NlY3VyZS1ST0xMT1VUX1RP*********nTVlwc2FveHRqOWxnTSUzRAo="
SESSION_STRING="1BJWap1sBuxJgoGdFww01wyaSMnq9G9tBGyhVZWzuEnY**********gW8JdbuVdR_QfAmDCEQ="
TARGET_CHANNEL="https://t.me/YourChannelID"
TARGET_CHANNEL_USERNAME="@YourChannelID"
TELEGRAM_TOKEN="88****33:AAGDRhUo******gKfTpYSvF0k"
ADMIN_CHAT_ID="7827********781"
ADMIN_PANEL_PASSWORD="YourPass"
LINK_TTL_HOURS="24"
PUBLIC_BASE_URL="https://YourPublicBaseUrl"

```

4. **Redeploy And Enjoy!**

---
## 🔐 Text to Base64 Converter (for Cookie Encoding)

[Click here to open the Base64 conversion tool](https://amirh-ti.github.io/Base64Kit/)

> 🛡️ **Security Note:** Don't worry about the safety of your data! All conversion operations are performed **entirely locally (client-side)** in your own browser. No data is ever sent to a server, stored, or logged — your information is never kept anywhere.

> 🔍 **Code Transparency:** For your peace of mind, you can review the complete source code of this tool in the repository below:
>
> [View source code on GitHub](https://github.com/amirh-ti/Base64Kit/)
---
