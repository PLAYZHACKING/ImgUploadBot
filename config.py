import os
from uploaders import imgbb, postimages, freeimage

ADMIN_IDS = os.environ.get("ADMIN_IDS")


class MONGO:
    URI = os.environ.get("MONGO_URI")
    NAME = os.environ.get("MONGO_DB_NAME", "img_uploadbot")


class BOT:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # DO NOT EDIT ANYTHING IN UPLOADERS_AVAILABLE #
    UPLOADERS_AVAILABLE = {
        "imgbb": imgbb,
        "postimages": postimages,
        "freeimage": freeimage,
    }
    ###############################################


class WEB:
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://img-upload-bot-amber.vercel.app/")


class FORCE_SUB:
    FORCE_SUB = os.environ.get("FORCE_SUB", True)
    CHANNEL_USERNAME = os.environ.get("FORCE_SUB_CHANNEL", "@PLAYZ_HACKING")


