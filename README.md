<img src="./banner.jpg" alt="Banner" style="width:100%; height:auto;">

A powerful Telegram bot that uploads images to multiple hosting services and provides shareable links instantly.

![Python](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=FFE873)
![Flask](https://img.shields.io/badge/flask-212121?style=for-the-badge&logo=flask&logoColor=F9F9F9)
![MongoDB](https://img.shields.io/badge/MongoDB-001E2B?style=for-the-badge&logo=mongodb&logoColor=00ED64)
![Vercel](https://img.shields.io/badge/vercel-000000?style=for-the-badge&logo=vercel&logoColor=FFFFFF)
![Telegram](https://img.shields.io/badge/telegram-000000?style=for-the-badge&logo=telegram&logoColor=FFFFFF)

## ✨ Features

- 📤 **Multiple Image Hosting Services**: Upload to ImgBB, FreeImage, or PostImages
- 🔄 **User Preferences**: Remember each user's preferred hosting service
- 🔐 **Force Subscription**: Optional channel subscription requirement
- 📊 **User Tracking**: Track served users in MongoDB
- ⚡ **Serverless Deployment**: Deploy on Vercel with zero maintenance
- 🌐 **Webhook Integration**: Real-time Telegram updates via webhook
- 💾 **Database**: MongoDB integration for persistence
- 🎨 **Beautiful UI**: Inline keyboard buttons for seamless navigation

## 📋 Prerequisites

Before you begin, ensure you have:

- **Telegram Account** - For creating a bot
- **Vercel Account** - For hosting (free tier available)
- **MongoDB Account** - For database (free tier M0 available)

## 🚀 Quick Start

### 1️⃣ Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/start` and follow the prompts
3. Send `/newbot` to create a new bot
4. Follow the setup wizard and save your:
   - **Bot Token** (will look like `123456789:ABCdefGHIjklmnoPQRstuvWXYZ`)

### 2️⃣ MongoDB Setup

#### Refer to this video for detailed step by step tutorial: https://youtu.be/SMXbGrKe5gM (Not my video, I just think he explained it well.)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Create a new cluster (M0 Free tier)
4. Create a database user with username and strong password
5. Go to network tab and allow from everywhere
6. Get your connection string:
   - Click "Connect" → "Connect your application"
   - Copy the MongoDB URI: `mongodb+srv://username:password@cluster.mongodb.net/`

### 3️⃣ Deploy on Vercel

#### Using Vercel Dashboard (Recommended for Beginners)

1. **Fork the Repository**
   - Go to [GitHub Repository](https://github.com/XylonBots/ImgUploadBot)
   - Click "Fork" in the top right corner

2. **Connect to Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Sign up or log in with GitHub
   - Click "Add New..." → "Project"
   - Select your forked repository
   - Click "Import"

3. **Configure Environment Variables**
   - In the "Environment Variables" section, add the following:

   | Variable | Value | Example |
   |----------|-------|---------|
   | `MONGO_URI` | Your MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
   | `MONGO_DB_NAME` | Database name | `img_uploadbot` |
   | `BOT_TOKEN` | Your bot token from @BotFather | `123456789:ABCdefGHIjklmnoPQRst` |
   | `WEBHOOK_URL` | Your Vercel app URL (**YOU WILL GET IT AFTER FIRST DEPLOYING THE PROJECT. So leave it empty for now.**) | `https://your-app-name.vercel.app/api/webhook` |
   | `ADMIN_IDS` | Your Telegram user ID (without spaces) | `123456789,987654321` |
   | `FORCE_SUB` | Enable force subscription | `true` or `false` |
   | `FORCE_SUB_CHANNEL` | Channel username for subscription | `@YourChannelName` |

   > **Note**: Get your Telegram user ID by messaging [@userinfobot](https://t.me/userinfobot)

4. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete (usually 1-2 minutes)
   - Copy your Vercel deployment URL (e.g., `https://your-app-name.vercel.app`)
   - **Go to settings > Go to `Environment Variables` > Edit `WEBHOOK_URL` with `https://your-app-name.vercel.app/api/webhook` (don't forget to add `/api/webhook` after your vercel deployment URL) > Click save > (a popup will apear) On that popup click `Redeploy`**

### 4️⃣ Set Webhook

After deployment, set your bot's webhook to receive updates:

**Option A: Using Telegram Bot API (Recommended)**

Send a GET reques to (just open it in browser):
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<VERCEL_DEPLOYMENT_URL>/api/webhook
```
> Replace <YOUR_BOT_TOKEN> with your `BOT TOKEN` and <VERCEL_DEPLOYMENT_URL> with your `DEPLOYMENT URL`

**Option B: Using Python**

```python
import requests

bot_token = "YOUR_BOT_TOKEN"
webhook_url = "https://your-app-name.vercel.app"

response = requests.get(
    f"https://api.telegram.org/bot{bot_token}/setWebhook",
    params={"url": f"{webhook_url}/api/webhook"}
)
print(response.json())
```

**Option C: Using curl**

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<VERCEL_DEPLOYMENT_URL>/api/webhook"
```
> Replace <YOUR_BOT_TOKEN> with your `BOT TOKEN` and <VERCEL_DEPLOYMENT_URL> with your `DEPLOYMENT URL`

✅ **Expected Response:**
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

### 6️⃣ Test Your Bot

1. Open Telegram
2. Open your bot
3. Send `/start`
4. Try uploading an image
5. Select your preferred hosting service

## 📁 Project Structure

```
ImgUploadBot/
├── api/
│   └── index.py                 # Main Flask app & webhook handler
├── database/
│   ├── __init__.py
│   ├── settings.py              # User settings management
│   └── users.py                 # User tracking
├── methods/
│   ├── inline_keyboard.py       # Keyboard UI components
│   └── updates.py               # Telegram Bot API wrapper
├── uploaders/
│   ├── __init__.py
│   ├── imgbb.py                 # ImgBB uploader
│   ├── freeimage.py             # FreeImage uploader
│   └── postimages.py            # PostImages uploader
├── config.py                    # Configuration & environment variables
├── utils.py                     # Helper functions & messages
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel configuration
└── example.env                  # Example environment variables
```

## ⚙️ Environment Variables Explained

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB_NAME=img_uploadbot

# Telegram bot credentials
BOT_TOKEN=1234567890:ABCdefGHIjklmnoPQRstuvWXYZ1234567

# Deployment
WEBHOOK_URL=https://your-app-name.vercel.app/api/webhook

# Admin settings
ADMIN_IDS=123456789,987654321

# Force subscription settings
FORCE_SUB=true
FORCE_SUB_CHANNEL=@YourChannelName
```

## 🎮 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| Button: ⚙️ **Change Hosting** | Switch between uploading services |
| Button: 📢 **Join Channel** | Join the bot's channel |
| Button: ↗️ **Source Code** | View the GitHub repository |

## 🔄 How It Works

1. **User sends image** → Bot receives it via Telegram webhook
2. **Download image** → Bot downloads the image to memory
3. **Select uploader** → Uses user's saved preference or ImgBB as default
4. **Upload image** → Image uploaded to selected service
5. **Send link** → Bot sends shareable link back to user
6. **Save preference** → User's choice stored in MongoDB for next time

**Dependencies:**
- **beautifulsoup4**: HTML parsing
- **Flask**: Web framework
- **pymongo**: MongoDB driver
- **Requests**: HTTP library
- **UserAgentReplica**: User agent spoofing

## 🐛 Troubleshooting

### Bot not responding to messages

- ✅ Check if webhook is correctly set
- ✅ Verify bot token is correct
- ✅ Ensure Vercel deployment is active

```bash
# Check webhook status
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### MongoDB connection errors

- ✅ Verify MONGO_URI format is correct
- ✅ Check if database user password is URL-encoded
- ✅ Ensure IP whitelist includes Vercel servers (set to 0.0.0.0/0 if on free tier)

### Webhook not received

- ✅ Make sure Vercel app is deployed and active
- ✅ Check Vercel logs for errors
- ✅ Verify webhook URL is publicly accessible

## 📊 Features in Detail

### 🎯 User Preferences System
- Each user's hosting preference is saved in MongoDB
- Default uploader is ImgBB if no preference is set
- Users can change their preference anytime

### 🔐 Force Subscription
Enable this feature to require users to join a channel before using the bot. Configure via:
- `FORCE_SUB=true`
- `FORCE_SUB_CHANNEL=@YourChannelName`

### 👨‍💼 Admin Broadcasting
Admins (configured in `ADMIN_IDS`) can broadcast messages to all served users. When an admin sends a message, All commands gets pinned for better experience for admin.

## 📈 Scaling & Performance

- **Serverless**: Auto-scales with Vercel
- **Database**: MongoDB free tier supports ~500MB storage
- **Requests**: Flask handles concurrent requests efficiently
- **Rate Limits**: Telegram Bot API has rate limiting (~30 messages/second)

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **GitHub**: [TheHritu](https://github.com/TheHritu)
- **Telegram Channel**: [@XylonBots](https://t.me/XylonBots)
- **Report Issues**: [GitHub Issues](https://github.com/XylonBots/ImgUploadBot/issues)

## 📞 Support

- ⭐ **Star** the repository if you find it helpful
- 🐛 **Report bugs** via GitHub Issues
- 💬 **Discuss** improvements in GitHub Discussions
- 📧 **Contact** **[Hritu](https://t.me/Xylon_Hritu)** maintainers on Telegram 

---

<div align="center">

**Made with ❤️ by [XylonBots](https://github.com/XylonBots)**

</div>