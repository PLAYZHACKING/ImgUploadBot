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
                        "url": "https://t.me/XylonBots",
                    }
                ],
                [
                    {
                        "text": "↗️ Source Code",
                        "url": "https://github.com/XylonBots/ImgUploadBot",
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
<b>🚀 Welcome to the Image Uploader Bot!</b>

I'm here to help you upload images and get a shareable link in seconds.

<b>How it works:</b>
• Send me any <b>image</b> as a photo or document.
• I'll upload it using your chosen service.
• You'll receive a direct URL to share or download.

<b>⚙️ Change Hosting:</b> Tap the button below to select your preferred hosting to upload your image.

Let's get started — send me an image now!
"""
    HOSTINGS_MSG = """
<b>⚙️ Current uploader:</b> <code>{0}</code>

<i>Choose your preferred uploader from the buttons below.</i>
"""
    FORCE_SUB_MSG = """
<b>🔒 Access Restricted</b>

To use this bot, you need to join our official channel first.

<b>📢 Channel:</b> {0}

<i>Once you've joined, please send your request again.</i>
"""
