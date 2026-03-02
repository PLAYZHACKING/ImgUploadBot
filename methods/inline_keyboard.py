from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class InlineKeyboardButton:
    """
    Represents one button of an inline keyboard.

    """

    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None
    icon_custom_emoji_id: Optional[str] = None
    style: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary expected by Telegram API, removing None values."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


class InlineKeyboardMarkup:
    """
    Builds the inline keyboard markup.
    Use the static factory methods to create common keyboards.
    """

    def __init__(self, buttons: List[List[InlineKeyboardButton]]):
        """
        Args:
            buttons: A list of rows, each row is a list of InlineKeyboardButton.
        """
        self.buttons = buttons

    def to_dict(self) -> Dict[str, List]:
        """Convert to the format required by Telegram's reply_markup."""
        return {
            "inline_keyboard": [[btn.to_dict() for btn in row] for row in self.buttons]
        }

    @staticmethod
    def button_grid(grid: List[List[Dict[str, str]]]) -> "InlineKeyboardMarkup":
        """
        Create a keyboard from a grid of dictionaries.
        Each dict must contain 'text' and one action key.
        Example:
            grid = [
                [{"text": "Yes", "callback_data": "yes"}],
                [{"text": "Help", "url": "https://example.com"}]
            ]
        """
        rows = []
        for row in grid:
            btn_row = []
            for btn_dict in row:
                # Pop the text, rest are action parameters
                text = btn_dict.pop("text")
                # Create button with the remaining keys as kwargs
                btn = InlineKeyboardButton(text=text, **btn_dict)
                btn_row.append(btn)
            rows.append(btn_row)
        return InlineKeyboardMarkup(rows)


# ========== Common Button Factories ==========


class InlineKeyboard:
    """Factory for creating common inline keyboard buttons."""

    @staticmethod
    def callback(text: str, data: str) -> InlineKeyboardButton:
        """Button that sends a callback query."""
        return InlineKeyboardButton(text=text, callback_data=data)

    @staticmethod
    def url(text: str, url: str) -> InlineKeyboardButton:
        """Button that opens a URL."""
        return InlineKeyboardButton(text=text, url=url)
