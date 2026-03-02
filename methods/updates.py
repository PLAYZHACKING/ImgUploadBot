"""
Telegram Bot API Wrapper

A professional, production-ready wrapper for the Telegram Bot API using the requests library.
Supports all major bot methods with proper error handling, logging, and type hints.
"""

import json
import logging
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, BinaryIO, Dict, List, Optional, Union

import requests

# Configure module-level logger
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    A Python client for the Telegram Bot API.

    All methods return the parsed JSON result from Telegram (the 'result' field)
    or raise an exception on error.
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.telegram.org/bot",
        timeout: int = 30,
    ) -> None:
        """
        Initialize the bot with your access token.

        Args:
            token: Bot token from @BotFather.
            base_url: Base URL for the API (useful for self-hosted APIs).
            timeout: Request timeout in seconds.
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.logger = logger

    def _request(
        self,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        include_url: bool = False,
    ) -> Any:
        url = f"{self.base_url}{self.token}/{method}"

        # Convert any dict or list values to JSON strings
        if data:
            data = data.copy()  # avoid mutating the original
            for key, value in list(data.items()):
                if isinstance(value, (dict, list)):
                    data[key] = json.dumps(value)

        self.logger.debug("Request: %s %s", method, data)

        try:
            response = self.session.post(
                url, data=data, files=files, timeout=self.timeout
            )
            result = response.json()
            if include_url and method == "getFile":
                try:
                    result["url"] = (
                        lambda p: f"{p.scheme}://{p.hostname}/file/bot{self.token}/"
                    )(urlparse(url)) + result["result"]["file_path"]
                except:
                    pass
                return result
            return result

        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed: %s", e)
            raise
        except ValueError as e:
            self.logger.error("Invalid JSON response: %s", e)
            raise

    def _prepare_file(
        self, file_input: Union[str, Path, BinaryIO]
    ) -> Union[str, BinaryIO]:
        """
        Convert a file input (path or file-like) to a value suitable for the API.
        If it's a string or Path, open the file and return the file object.
        Otherwise, return the file object as is.

        Args:
            file_input: File path (str/Path) or a binary file-like object.

        Returns:
            Either a string (file_id/URL) or an open file object.
        """
        if isinstance(file_input, (str, Path)):
            # Open file in binary mode; it will be closed by requests after upload
            return open(file_input, "rb")
        return file_input

    # ==================== Basic Methods ====================

    def get_me(self) -> Dict[str, Any]:
        """Get basic information about the bot."""
        return self._request("getMe")

    # ==================== Sending Messages ====================

    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message.

        Args:
            chat_id: Unique identifier for the target chat or username.
            text: Text of the message.
            parse_mode: 'MarkdownV2', 'HTML', or None.
            disable_web_page_preview: Disable link previews.
            disable_notification: Send silently.
            reply_to_message_id: If set, reply to this message.
            reply_markup: Additional interface options (inline keyboard, etc.).

        Returns:
            The sent Message object.
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("sendMessage", data)

    def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, Path, BinaryIO],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a photo.

        Args:
            chat_id: Unique identifier for the target chat.
            photo: File_id, URL, or file path / file-like object.
            caption: Photo caption.
            parse_mode: Markdown or HTML for caption.
            disable_notification: Send silently.
            reply_to_message_id: If set, reply to this message.
            reply_markup: Inline keyboard etc.

        Returns:
            The sent Message object.
        """
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}

        if isinstance(photo, (str, Path)) and not str(photo).startswith(
            ("http://", "https://")
        ):
            # Assume local file path
            files = {"photo": self._prepare_file(photo)}
            # photo is not in data, only in files
            return self._request("sendPhoto", data, files)
        elif isinstance(photo, str):
            # It's a file_id or URL
            data["photo"] = photo
            return self._request("sendPhoto", data)
        else:
            # Assume file-like object
            files = {"photo": photo}
            return self._request("sendPhoto", data, files)

    def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[str, Path, BinaryIO],
        thumb: Optional[Union[str, Path, BinaryIO]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a general file.

        Args:
            chat_id: Target chat.
            document: File_id, URL, or local file path / file-like.
            thumb: Thumbnail.
            caption: Document caption.
            parse_mode: Markdown or HTML.
            disable_notification: Send silently.
            reply_to_message_id: Reply to a message.
            reply_markup: Inline keyboard.

        Returns:
            The sent Message object.
        """
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}

        files = {}
        if isinstance(document, (str, Path)) and not str(document).startswith(
            ("http://", "https://")
        ):
            files["document"] = self._prepare_file(document)
        elif isinstance(document, str):
            data["document"] = document
        else:
            files["document"] = document

        if thumb:
            if isinstance(thumb, (str, Path)) and not str(thumb).startswith(
                ("http://", "https://")
            ):
                files["thumb"] = self._prepare_file(thumb)
            elif isinstance(thumb, str):
                data["thumb"] = thumb
            else:
                files["thumb"] = thumb

        return self._request("sendDocument", data, files)

    def send_chat_action(self, chat_id: Union[int, str], action: str) -> bool:
        """
        Send a chat action (typing, upload_photo, etc.).
        Returns True on success.
        """
        return self._request("sendChatAction", {"chat_id": chat_id, "action": action})

    # ==================== Getting Updates ====================

    def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Receive incoming updates using long polling.

        Args:
            offset: Identifier of the first update to be returned.
            limit: Limits the number of updates to be retrieved.
            timeout: Timeout in seconds for long polling.
            allowed_updates: List of update types to receive.

        Returns:
            An array of Update objects.
        """
        data = {
            "offset": offset,
            "limit": limit,
            "timeout": timeout,
            "allowed_updates": allowed_updates,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("getUpdates", data)

    # ==================== Webhook Management ====================

    def set_webhook(
        self,
        url: str,
        certificate: Optional[Union[str, Path, BinaryIO]] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = [],
        drop_pending_updates: Optional[bool] = None,
        secret_token: Optional[str] = None,
    ) -> bool:
        """
        Set a webhook to receive updates via HTTPS POST.

        Returns True on success.
        """
        data = {
            "url": url,
            "ip_address": ip_address,
            "max_connections": max_connections,
            "allowed_updates": allowed_updates,
            "drop_pending_updates": drop_pending_updates,
            "secret_token": secret_token,
        }
        data = {k: v for k, v in data.items() if v is not None}

        files = None
        if certificate:
            if isinstance(certificate, (str, Path)):
                files = {"certificate": open(certificate, "rb")}
            else:
                files = {"certificate": certificate}

        return self._request("setWebhook", data, files)

    def delete_webhook(self, drop_pending_updates: Optional[bool] = None) -> bool:
        """Remove webhook integration."""
        data = {}
        if drop_pending_updates is not None:
            data["drop_pending_updates"] = drop_pending_updates
        return self._request("deleteWebhook", data)

    def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook status."""
        return self._request("getWebhookInfo")

    # ==================== File Management ====================

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get basic info about a file and prepare it for downloading.

        Returns:
            A File object.
        """
        return self._request("getFile", {"file_id": file_id}, include_url=True)

    # ==================== Message Editing ====================

    def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bool]:
        """
        Edit text messages sent by the bot or via the bot (for inline bots).

        Returns the edited Message or True if inline message was edited.
        """
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("editMessageText", data)

    def edit_message_caption(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bool]:
        """Edit captions of messages."""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("editMessageCaption", data)

    def edit_message_media(
        self,
        media: Dict[str, Any],
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bool]:
        """
        Edit animation, audio, document, photo, or video messages.

        media: A dictionary similar to the one used in sendMediaGroup, with keys:
               'type', 'media', 'caption', 'parse_mode', etc.
               If 'media' is a local file, it will be uploaded.
        """
        # Prepare file if needed
        files = {}
        media_value = media.get("media")
        if isinstance(media_value, (str, Path)) and not str(media_value).startswith(
            ("http://", "https://")
        ):
            # Local file
            file_key = "media_file"
            files[file_key] = self._prepare_file(media_value)
            media_copy = media.copy()
            media_copy["media"] = f"attach://{file_key}"
            media_json = media_copy
        elif isinstance(media_value, str):
            # file_id or URL
            media_json = media
        else:
            # file-like
            file_key = "media_file"
            files[file_key] = media_value
            media_copy = media.copy()
            media_copy["media"] = f"attach://{file_key}"
            media_json = media_copy

        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "media": media_json,  # will be JSON-encoded
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}
        import json

        data["media"] = json.dumps(data["media"])

        return self._request("editMessageMedia", data, files if files else None)

    def edit_message_reply_markup(
        self,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bool]:
        """Edit only the reply markup of a message."""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_message_id": inline_message_id,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("editMessageReplyMarkup", data)

    def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """Delete a message."""
        return self._request(
            "deleteMessage", {"chat_id": chat_id, "message_id": message_id}
        )

    # ==================== Forward & Copy ====================

    def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        disable_notification: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Forward a message of any kind."""
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("forwardMessage", data)

    def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Copy messages of any kind."""
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("copyMessage", data)

    # ==================== Chat Management ====================

    def ban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        until_date: Optional[int] = None,
        revoke_messages: Optional[bool] = None,
    ) -> bool:
        """Ban a user from a group, supergroup, or channel."""
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "until_date": until_date,
            "revoke_messages": revoke_messages,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("banChatMember", data)

    def unban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        only_if_banned: Optional[bool] = None,
    ) -> bool:
        """Unban a previously banned user."""
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("unbanChatMember", data)

    def restrict_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        permissions: Dict[str, bool],
        until_date: Optional[int] = None,
    ) -> bool:
        """Restrict a user in a supergroup."""
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": permissions,
            "until_date": until_date,
        }
        data = {k: v for k, v in data.items() if v is not None}
        import json

        data["permissions"] = json.dumps(data["permissions"])
        return self._request("restrictChatMember", data)

    def promote_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        is_anonymous: Optional[bool] = None,
        can_manage_chat: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_manage_video_chats: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        can_change_info: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
    ) -> bool:
        """Promote or demote a user in a supergroup or channel."""
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "is_anonymous": is_anonymous,
            "can_manage_chat": can_manage_chat,
            "can_post_messages": can_post_messages,
            "can_edit_messages": can_edit_messages,
            "can_delete_messages": can_delete_messages,
            "can_manage_video_chats": can_manage_video_chats,
            "can_restrict_members": can_restrict_members,
            "can_promote_members": can_promote_members,
            "can_change_info": can_change_info,
            "can_invite_users": can_invite_users,
            "can_pin_messages": can_pin_messages,
            "can_manage_topics": can_manage_topics,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("promoteChatMember", data)

    def leave_chat(self, chat_id: Union[int, str]) -> bool:
        """Leave a group, supergroup, or channel."""
        return self._request("leaveChat", {"chat_id": chat_id})

    def get_chat(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Get up‑to‑date information about a chat."""
        return self._request("getChat", {"chat_id": chat_id})

    def get_chat_administrators(self, chat_id: Union[int, str]) -> List[Dict[str, Any]]:
        """Get a list of administrators in a chat."""
        return self._request("getChatAdministrators", {"chat_id": chat_id})

    def get_chat_members_count(self, chat_id: Union[int, str]) -> int:
        """Get the number of members in a chat."""
        return self._request("getChatMembersCount", {"chat_id": chat_id})

    def get_chat_member(self, chat_id: Union[int, str], user_id: int) -> Dict[str, Any]:
        """Get information about a specific member of a chat."""
        return self._request("getChatMember", {"chat_id": chat_id, "user_id": user_id})

    def set_chat_title(self, chat_id: Union[int, str], title: str) -> bool:
        """Change the title of a chat."""
        return self._request("setChatTitle", {"chat_id": chat_id, "title": title})

    def set_chat_description(
        self, chat_id: Union[int, str], description: Optional[str] = None
    ) -> bool:
        """Change the description of a group, supergroup, or channel."""
        data = {"chat_id": chat_id}
        if description is not None:
            data["description"] = description
        return self._request("setChatDescription", data)

    def set_chat_photo(
        self, chat_id: Union[int, str], photo: Union[str, Path, BinaryIO]
    ) -> bool:
        """Set a new profile photo for the chat."""
        if isinstance(photo, (str, Path)):
            files = {"photo": self._prepare_file(photo)}
        else:
            files = {"photo": photo}
        return self._request("setChatPhoto", {"chat_id": chat_id}, files)

    def delete_chat_photo(self, chat_id: Union[int, str]) -> bool:
        """Delete a chat photo."""
        return self._request("deleteChatPhoto", {"chat_id": chat_id})

    def pin_chat_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        disable_notification: Optional[bool] = None,
    ) -> bool:
        """Pin a message in a group, supergroup, or channel."""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("pinChatMessage", data)

    def unpin_chat_message(
        self, chat_id: Union[int, str], message_id: Optional[int] = None
    ) -> bool:
        """Unpin a message in a chat."""
        data = {"chat_id": chat_id}
        if message_id is not None:
            data["message_id"] = message_id
        return self._request("unpinChatMessage", data)

    def unpin_all_chat_messages(self, chat_id: Union[int, str]) -> bool:
        """Unpin all pinned messages in a chat."""
        return self._request("unpinAllChatMessages", {"chat_id": chat_id})

    # ==================== Inline Mode ====================

    def answer_inline_query(
        self,
        inline_query_id: str,
        results: List[Dict[str, Any]],
        cache_time: Optional[int] = None,
        is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        button: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send answers to an inline query."""
        data = {
            "inline_query_id": inline_query_id,
            "results": results,
            "cache_time": cache_time,
            "is_personal": is_personal,
            "next_offset": next_offset,
            "button": button,
        }
        data = {k: v for k, v in data.items() if v is not None}
        import json

        data["results"] = json.dumps(data["results"])
        if "button" in data:
            data["button"] = json.dumps(data["button"])
        return self._request("answerInlineQuery", data)

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> bool:
        """Send answers to callback queries sent from inline keyboards."""
        data = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
            "url": url,
            "cache_time": cache_time,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return self._request("answerCallbackQuery", data)
