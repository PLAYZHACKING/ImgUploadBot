import io
import random
import string
import logging
import requests
from flask import Flask, jsonify, request
from typing import Any, Dict, Optional, Tuple

# Fix imports - remove the relative imports and use absolute ones
try:
    from config import ADMIN_IDS, BOT, FORCE_SUB, WEB
    from utils import BOARD, TEXT
    from methods.updates import TelegramBot
    from database.users import add_served_user, get_served_users
    from database.settings import get_user_settings, update_user_setting
except ImportError:
    # For serverless deployment, try alternative import paths
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import ADMIN_IDS, BOT, FORCE_SUB, WEB
    from utils import BOARD, TEXT
    from methods.updates import TelegramBot
    from database.users import add_served_user, get_served_users
    from database.settings import get_user_settings, update_user_setting

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def generate_random_filename(extension: str = ".jpg") -> str:
    """Generate a random filename with the given extension."""
    first_char = random.choice(string.ascii_letters)
    rest = "".join(random.choices(string.ascii_letters + string.digits, k=7))
    return f"{first_char}{rest}{extension}"


def download_image_to_bytesio(
    url: str, filename: Optional[str] = None
) -> Tuple[io.BytesIO, str]:
    """Download an image from a URL and return it as a BytesIO buffer."""
    if filename is None:
        filename = generate_random_filename()

    response = requests.get(url, stream=True, timeout=8)
    response.raise_for_status()
    buffer = io.BytesIO()
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            buffer.write(chunk)
    buffer.seek(0)
    buffer.name = filename
    return buffer, filename


class TelegramBotWebhook:
    """Handles incoming Telegram updates."""

    def __init__(self, bot_token: str) -> None:
        self.bot = TelegramBot(bot_token)
        self.awaiting_broadcast = {}
        logger.info("TelegramBotWebhook initialized.")

    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Manually set the Telegram bot webhook."""
        try:
            full_url = webhook_url.rstrip("/") + "/api/webhook"
            result = self.bot.set_webhook(url=full_url)
            if result.get("ok"):
                logger.info(f"Webhook successfully set to {full_url}")
            else:
                logger.error(f"Failed to set webhook: {result.get('description')}")
            return result
        except Exception as e:
            logger.exception(f"Exception while setting webhook: {e}")
            return {"error": str(e)}

    def process_update(self, update: Dict[str, Any]) -> Tuple[Any, int]:
        """Handle incoming Telegram updates."""
        try:
            if "message" in update:
                self._handle_message(update["message"])
            elif "callback_query" in update:
                self._handle_callback_query(update["callback_query"])
            else:
                logger.debug("Unsupported update type received.")
        except Exception as e:
            logger.exception(f"Unhandled exception while processing update: {e}")

        return jsonify({"status": "ok"}), 200

    def get_webhook_info(self) -> Tuple[Any, int]:
        """Return current webhook status."""
        try:
            info = self.bot.get_webhook_info()
            return jsonify(info), 200
        except Exception as e:
            logger.exception("Failed to retrieve webhook info")
            return jsonify({"error": str(e)}), 500

    def _is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin."""
        return str(user_id) in ADMIN_IDS.split(",")

    def _handle_admin_message(self, chat_id: int, message: Dict[str, Any]) -> bool:
        """Process admin commands and broadcast content. Returns True if message was consumed."""
        if not "pinned_message" in str(self.bot.get_chat(chat_id)):
            msg_to_pin = self.bot.send_message(
                chat_id=chat_id,
                text="/broadcast - broadcast any message \n/fwdcast - broadcast the forwarded message \n/cancel - aborts an ongoing broadcast \n/status - get total number of users in the bot",
            )
            self.bot.pin_chat_message(
                chat_id=chat_id, message_id=msg_to_pin["result"]["message_id"]
            )
        text = message.get("text", "")
        if text.startswith("/cancel"):
            if chat_id in self.awaiting_broadcast:
                del self.awaiting_broadcast[chat_id]
                self.bot.send_message(chat_id, "Broadcast cancelled.")
            else:
                self.bot.send_message(chat_id, "No active broadcast to cancel.")
            return True

        if chat_id in self.awaiting_broadcast:
            mode = self.awaiting_broadcast.pop(chat_id)
            self._broadcast_message(chat_id, message, mode)
            return True

        if text.startswith("/broadcast"):
            self.awaiting_broadcast[chat_id] = "copy"
            self.bot.send_message(
                chat_id=chat_id,
                text="Send me the message you want to broadcast (any type). I will copy it to all users.",
                parse_mode="HTML",
            )
            return True

        if text.startswith("/fwdcast"):
            self.awaiting_broadcast[chat_id] = "forward"
            self.bot.send_message(
                chat_id=chat_id,
                text="Send me the message you want to forward to all users. I will forward it.",
                parse_mode="HTML",
            )
            return True
        
        if text.startswith("/status"):
            try:
                users = get_served_users()
                self.bot.send_message(chat_id, f"Total served users: {len(users)}")
            except Exception as e:
                logger.error(f"Failed to get served users: {e}")
                self.bot.send_message(chat_id, "Failed to retrieve user list.")
            return True

        return False

    def _broadcast_message(
        self, admin_chat_id: int, message: Dict[str, Any], mode: str
    ) -> None:
        """Broadcast the given message to all served users."""
        try:
            users = get_served_users()
        except Exception as e:
            logger.error(f"Failed to get served users: {e}")
            self.bot.send_message(admin_chat_id, "Failed to retrieve user list.")
            return

        if not users:
            self.bot.send_message(admin_chat_id, "No users to broadcast to.")
            return

        self.bot.send_message(admin_chat_id, f"Broadcasting to {len(users)} users...")

        success = 0
        failed = 0
        from_chat_id = message["chat"]["id"]
        message_id = message["message_id"]

        for user_id in users:
            try:
                if mode == "copy":
                    self.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=from_chat_id,
                        message_id=message_id,
                    )
                elif mode == "forward":
                    self.bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=from_chat_id,
                        message_id=message_id,
                    )
                success += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {user_id}: {e}")
                failed += 1

        self.bot.send_message(
            admin_chat_id, f"Broadcast completed.\nSuccess: {success}\nFailed: {failed}"
        )

    def _ensure_user_tracked(self, chat_id: int) -> None:
        """Add user to served users database if not already present."""
        try:
            add_served_user(chat_id)
        except Exception as e:
            logger.error(f"Failed to add served user {chat_id}: {e}")

    def _check_force_subscription(self, chat_id: int) -> bool:
        """Check if the user is subscribed to the required channel."""
        if not FORCE_SUB.FORCE_SUB:
            return True

        channel = FORCE_SUB.CHANNEL_USERNAME
        if not channel:
            return True

        try:
            result = self.bot.get_chat_member(chat_id=channel, user_id=chat_id)
            if result.get("ok") and result.get("result", {}).get("status") in [
                "member",
                "administrator",
                "creator",
            ]:
                return True
            else:
                return False
        except Exception as e:
            return False

    def _send_force_sub_prompt(self, chat_id: int) -> None:
        """Send a message asking the user to join the channel."""
        try:
            self.bot.send_photo(
                chat_id=chat_id,
                photo="https://t.me/xylon_bots/7",
                caption=TEXT.FORCE_SUB_MSG.format(FORCE_SUB.CHANNEL_USERNAME),
                reply_markup=BOARD.FORCE_SUB_KEYBOARD(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send force sub prompt to {chat_id}: {e}")

    def _handle_message(self, message: Dict[str, Any]) -> None:
        chat_id = message["chat"]["id"]
        self._ensure_user_tracked(chat_id)
        if not self._check_force_subscription(chat_id):
            self._send_force_sub_prompt(chat_id)
            return
        if self._is_admin(chat_id):
            if self._handle_admin_message(chat_id, message):
                return
        if "text" in message:
            self._handle_text_message(chat_id, message)
        elif "photo" in message:
            self._handle_photo_message(chat_id, message)
        elif "document" in message:
            self._handle_document_message(chat_id, message)
        else:
            logger.debug(f"Unsupported message type from {chat_id}")

    def _handle_text_message(self, chat_id: int, message: Dict[str, Any]) -> None:
        """Respond to a text message with the start menu."""
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=TEXT.START_MSG,
                reply_markup=BOARD.START_KEYBOARD(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send start message to {chat_id}: {e}")

    def _handle_photo_message(self, chat_id: int, message: Dict[str, Any]) -> None:
        """Process a photo message, upload it, and return the URL."""
        try:
            sent_msg = self.bot.send_message(
                chat_id=chat_id,
                text="<i>Uploading your image...</i>",
                parse_mode="HTML",
                reply_to_message_id=message["message_id"],
            )
            sent_msg_id = sent_msg["result"]["message_id"]
        except Exception as e:
            logger.error(f"Failed to send upload status to {chat_id}: {e}")
            return

        photo = message["photo"][-1]
        self._process_and_upload_file(
            chat_id=chat_id,
            file_id=photo["file_id"],
            original_message_id=message["message_id"],
            temp_message_id=sent_msg_id,
            mime_type="image/jpeg",
            filename=None,
        )

    def _handle_document_message(self, chat_id: int, message: Dict[str, Any]) -> None:
        """Process a document that might be an image."""
        doc = message["document"]
        mime_type = doc.get("mime_type", "application/octet-stream")
        if not mime_type.startswith("image/"):
            logger.info(f"User {chat_id} sent non-image document: {mime_type}")
            return

        try:
            sent_msg = self.bot.send_message(
                chat_id=chat_id,
                text="<i>Uploading your image...</i>",
                parse_mode="HTML",
                reply_to_message_id=message["message_id"],
            )
            sent_msg_id = sent_msg["result"]["message_id"]
        except Exception as e:
            logger.error(f"Failed to send upload status to {chat_id}: {e}")
            return

        self._process_and_upload_file(
            chat_id=chat_id,
            file_id=doc["file_id"],
            original_message_id=message["message_id"],
            temp_message_id=sent_msg_id,
            mime_type=mime_type,
            filename=doc.get("file_name"),
        )

    def _process_and_upload_file(
        self,
        chat_id: int,
        file_id: str,
        original_message_id: int,
        temp_message_id: int,
        mime_type: str,
        filename: Optional[str],
    ) -> None:
        """Download a file from Telegram, upload it using the user's preferred uploader, and send the link."""
        try:
            file_info = self.bot.get_file(file_id)
            if not file_info.get("ok"):
                error_msg = file_info.get("description", "Unknown error")
                self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=temp_message_id,
                    text=f"<code>Failed to get file:</code> {error_msg}",
                    parse_mode="HTML",
                )
                return
        except Exception as e:
            logger.exception(f"Error getting file info for {file_id}")
            self._safe_edit_message(
                chat_id,
                temp_message_id,
                "An error occurred while processing your file.",
            )
            return

        file_url = file_info["url"]

        try:
            buffer, actual_filename = download_image_to_bytesio(file_url, filename)
        except requests.RequestException as e:
            logger.error(f"Failed to download image from {file_url}: {e}")
            self._safe_edit_message(
                chat_id, temp_message_id, "Failed to download the image."
            )
            return
        except Exception as e:
            logger.exception(f"Unexpected error downloading image")
            self._safe_edit_message(
                chat_id, temp_message_id, "An unexpected error occurred."
            )
            return

        try:
            user_settings = get_user_settings(chat_id)
            uploader_name = user_settings.get("uploader")
            if uploader_name not in BOT.UPLOADERS_AVAILABLE:
                logger.warning(
                    f"Invalid uploader '{uploader_name}' for user {chat_id}, using default."
                )
                uploader_name = next(iter(BOT.UPLOADERS_AVAILABLE))
            uploader = BOT.UPLOADERS_AVAILABLE[uploader_name]
        except Exception as e:
            logger.exception(f"Failed to get uploader for {chat_id}")
            self._safe_edit_message(
                chat_id, temp_message_id, "Failed to determine upload service."
            )
            return

        try:
            url = uploader(actual_filename, buffer, mime_type)
        except Exception as e:
            logger.exception(f"Upload failed for user {chat_id}")
            self._safe_edit_message(
                chat_id, temp_message_id, "Upload failed. Please try again later."
            )
            return

        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=url,
                reply_markup=BOARD.BACK_TO_MENU_KEYBOARD(),
                reply_to_message_id=original_message_id,
            )
        except Exception as e:
            logger.error(f"Failed to send upload result to {chat_id}: {e}")

        self._safe_delete_message(chat_id, temp_message_id)

    def _safe_edit_message(self, chat_id: int, message_id: int, text: str) -> None:
        """Safely edit a message, ignoring failures."""
        try:
            self.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=text
            )
        except Exception as e:
            logger.debug(f"Failed to edit message {message_id} for {chat_id}: {e}")

    def _safe_delete_message(self, chat_id: int, message_id: int) -> None:
        """Safely delete a message, ignoring failures."""
        try:
            self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.debug(f"Failed to delete message {message_id} for {chat_id}: {e}")

    def _handle_callback_query(self, callback_query: Dict[str, Any]) -> None:
        """Process a callback query (button press)."""
        chat_id = callback_query["message"]["chat"]["id"]
        message_id = callback_query["message"]["message_id"]
        data = callback_query.get("data")
        self._ensure_user_tracked(chat_id)
        if data == "setting":
            self._show_settings(chat_id, message_id)
        elif data == "back":
            self._show_start_menu(chat_id, message_id)
        elif data == "back_to_menu":
            self._send_start_menu(chat_id)
        elif data in BOT.UPLOADERS_AVAILABLE:
            self._update_uploader_setting(chat_id, message_id, data)
        else:
            logger.debug(f"Unknown callback data '{data}' from {chat_id}")

    def _show_settings(self, chat_id: int, message_id: int) -> None:
        """Edit the current message to show the settings panel."""
        try:
            user_settings = get_user_settings(chat_id)
            uploader_name = user_settings.get("uploader")
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=TEXT.HOSTINGS_MSG.format(uploader_name),
                reply_markup=BOARD.SETTING_KEYBOARD(chat_id),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to show settings for {chat_id}: {e}")

    def _show_start_menu(self, chat_id: int, message_id: int) -> None:
        """Edit the current message back to the start menu."""
        try:
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=TEXT.START_MSG,
                reply_markup=BOARD.START_KEYBOARD(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to show start menu for {chat_id}: {e}")

    def _send_start_menu(self, chat_id: int) -> None:
        """Send a new start menu message."""
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=TEXT.START_MSG,
                reply_markup=BOARD.START_KEYBOARD(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send start menu to {chat_id}: {e}")

    def _update_uploader_setting(
        self, chat_id: int, message_id: int, uploader: str
    ) -> None:
        """Update the user's preferred uploader and refresh the settings panel."""
        try:
            update_user_setting(chat_id, "uploader", uploader)
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=TEXT.HOSTINGS_MSG.format(uploader),
                reply_markup=BOARD.SETTING_KEYBOARD(chat_id),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to update uploader for {chat_id}: {e}")


if not BOT.BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in config.")
bot_handler = TelegramBotWebhook(BOT.BOT_TOKEN)


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """Vercel entry point for Telegram updates."""
    update = request.get_json(force=True, silent=True)
    if not update:
        logger.warning("Received empty or invalid JSON payload.")
        return jsonify({"status": "error", "reason": "Invalid payload"}), 400

    return bot_handler.process_update(update)


@app.route("/api/set-webhook", methods=["GET"])
def trigger_set_webhook():
    """
    Hit this endpoint manually from your browser after deploying to Vercel:
    https://your-vercel-app-url.vercel.app/api/set-webhook
    """
    if not WEB.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL is not set in config."}), 500

    result = bot_handler.set_webhook(WEB.WEBHOOK_URL)
    return jsonify(result), 200


@app.route("/api/webhook-info", methods=["GET"])
def webhook_info():
    """Vercel entry point to check webhook status."""
    return bot_handler.get_webhook_info()


# For local development
if __name__ == "__main__":
    app.run(debug=True, port=5000)
