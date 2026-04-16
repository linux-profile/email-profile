"""IO helpers: write parsed messages to disk as JSON or HTML files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from email_profile.serializers.email import EmailSerializer


PathLike = Union[str, Path]


class MessageDumper:
    """Writes an :class:`EmailSerializer` to disk in various formats.

    This is the *only* place that performs filesystem IO for messages.
    The serializer itself is a pure DTO.
    """

    def __init__(self, message: EmailSerializer) -> None:
        self.message = message

    def to_dict(self) -> dict:
        """Return a JSON-friendly dict (attachments stripped to metadata)."""
        data = self.message.model_dump(
            by_alias=True, mode="json", exclude={"attachments"}
        )
        data["attachments"] = [
            {"file_name": a.file_name, "content_type": a.content_type}
            for a in self.message.attachments
        ]
        return data

    def to_json(self, path: PathLike = "json", *, indent: int = 4) -> Path:
        """Write the message as <path>/<id>.json."""
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        out = target / f"{self.message.id}.json"
        out.write_text(json.dumps(self.to_dict(), indent=indent, default=str))
        return out

    def to_html(self, path: PathLike = "html") -> Path:
        """Write the HTML body as <path>/<id>/index.html."""
        target = Path(path) / str(self.message.id)
        target.mkdir(parents=True, exist_ok=True)
        out = target / "index.html"
        out.write_text(self.message.body_text_html or "")
        return out
