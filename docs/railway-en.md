### Step-by-Step Deployment

1. **Fork the repository**  
   Go to the [TeleTube GitHub repository](https://github.com/amirh-ti/TeleTube) and click the **Fork** button to create a copy under your own GitHub account.

2. **Create a new Railway project**  
   - Log in to [Railway](https://railway.com).  
   - Click **New Project** → **Deploy from GitHub repo**.  
   - Select your forked TeleTube repository from the list.

3. **Configure environment variables**  
   Railway automatically detects the service and prompts you to add variables. Add **all mandatory variables** from the [Configuration](#️-configuration) section (or copy them from `.env.example`):  
   - `TELEGRAM_TOKEN`  
   - `API_ID`  
   - `API_HASH`  
   - `SESSION_STRING`  
   - `TARGET_CHANNEL`  
   - `TARGET_CHANNEL_USERNAME`  
   - (Optional) `DOWNLOAD_DIR`, `COOKIES_FILE`, `AUTO_SELECT_TIMEOUT`  

   > ⚠️ **Important:** Do **not** commit your `.env` file to GitHub. Railway provides a secure **Variables** tab where you can paste these values directly.

4. **Deploy**  
   Railway will build the container and start the bot automatically. You can monitor the build and runtime logs from the **Deployments** tab.
