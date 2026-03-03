from methods.inline_keyboard import InlineKeyboardMarkup
from database.settings import get_user_settings
from config import BOT, FORCE_SUB


class BOARD:
    def START_KEYBOARD():
        return InlineKeyboardMarkup.button_grid(
            [
                [
                    {
                        "text": "⚙️ Change Hosting",
                        "callback_data": "setting",
                        "style": "primary",
                    }
                ],
                [
                    {
                        "text": "📢 Join Channel",
                        "url": "https://t.me/+1bpf2AXxDoM3NTI1",
                    }
                ],
                [
                    {
                        "text": "↗️ Join All Channels",
                        "url": "https://t.me/addlist/_wpSEUUOiM9lNzk1",
                        "style": "primary",
                    }
                ],
            ]
        ).to_dict()

    def SETTING_KEYBOARD(chat_id):
        user_settings = get_user_settings(chat_id)
        uploader = None
        if (
            "uploader" in user_settings
            and user_settings["uploader"] in BOT.UPLOADERS_AVAILABLE
        ):
            uploader = user_settings["uploader"]
        if uploader == None:
            uploader = "imgbb"
        return InlineKeyboardMarkup.button_grid(
            [
                [
                    {
                        "text": f"Imgbb" + (" ✅" if uploader == "imgbb" else ""),
                        "callback_data": "imgbb",
                        "style": "success" if uploader == "imgbb" else "primary",
                    }
                ],
                [
                    {
                        "text": "FreeImage"
                        + (" ✅" if uploader == "freeimage" else ""),
                        "callback_data": "freeimage",
                        "style": "success" if uploader == "freeimage" else "primary",
                    }
                ],
                [
                    {
                        "text": "PostImages"
                        + (" ✅" if uploader == "postimages" else ""),
                        "callback_data": "postimages",
                        "style": "success" if uploader == "postimages" else "primary",
                    }
                ],
                [
                    {
                        "text": "🔙 Back",
                        "callback_data": "back",
                        "style": "danger",
                    }
                ],
            ]
        ).to_dict()

    def BACK_TO_MENU_KEYBOARD():
        return InlineKeyboardMarkup.button_grid(
            [
                [
                    {
                        "text": "🔙 Back To menu",
                        "callback_data": "back_to_menu",
                    }
                ],
            ]
        ).to_dict()

    def FORCE_SUB_KEYBOARD():
        return InlineKeyboardMarkup.button_grid(
            [
                [
                    {
                        "text": "⭐ Join Channel",
                        "url": "https://t.me/"
                        + FORCE_SUB.CHANNEL_USERNAME.replace("@", ""),
                        "style": "success",
                    }
                ],
            ]
        ).to_dict()


class TEXT:
    START_MSG = """
<b>✨ Welcome to the <a href="https://t.me/playz_image_host_bot">PLAYZ Image Uploader</a></b>

<blockquote>
⚡ Fast • 🤍 Elegant • 🔐 Secure
</blockquote>

Upload your images effortlessly and receive a direct, shareable link within seconds.

<b>📌 How it works:</b>

<blockquote expandable>
📤 Send any <b>photo</b> or <b>image as document</b>  
☁️ Your image is securely processed  
🔗 Instantly receive a clean download link  
📱 Smooth performance across all platforms  

Designed for a refined and premium experience.
</blockquote>

<b>⚙️ Upload Settings:</b>  
Use the button below to choose your preferred hosting service.

<blockquote>
👑 Powered by <a href="https://t.me/PLAYZ_HACKING/15">Team Playz</a>
</blockquote>

Send your image to begin.
"""
    HOSTINGS_MSG = """
<b>⚙️ Upload Preferences</b>

<blockquote>
📡 Current Uploader:
<code>{0}</code>
</blockquote>

<blockquote expandable>
✨ Stable performance  
🔗 Instant link generation  
🔐 Secure upload handling  
🚀 Reliable speed  

Switch anytime as per your preference.
</blockquote>
"""
    FORCE_SUB_MSG = """
<b>🔒 Access Required</b>

<blockquote>
To continue using this service, you must join our official channels.
</blockquote>

<blockquote expandable>
Click below to join our all channels.

👉 <a href="https://t.me/addlist/_wpSEUUOiM9lNzk1">Click Me</a>

After joining:
• 🔁 Return to the bot  
• 📤 Send your image again  
• ✨ Enjoy uninterrupted access
</blockquote>

<blockquote>
👑 Powered by <a href="https://t.me/PLAYZ_HACKING/15">Team Playz</a>
</blockquote>
"""
