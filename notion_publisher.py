"""Utilities for publishing YouTube RSS feeds to Notion."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from html import unescape
from typing import Dict, List

import pytz
import requests

from config import Config


logger = logging.getLogger(__name__)


class NotionPublisher:
    """Publish formatted YouTube feed information to Notion."""

    NOTION_API_URL = "https://api.notion.com/v1/pages"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, config: Config):
        self.api_key = config.NOTION_API_KEY
        self.database_id = config.NOTION_DATABASE_ID
        self.page_title_prefix = config.NOTION_PAGE_TITLE_PREFIX
        self.date_property_name = config.NOTION_DATE_PROPERTY

        try:
            self.timezone = pytz.timezone(config.TIMEZONE)
        except Exception:  # pragma: no cover - fallback path
            logger.warning(
                "Invalid TIMEZONE provided. Falling back to UTC for Notion timestamps."
            )
            self.timezone = pytz.UTC

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Notion-Version": self.NOTION_VERSION,
            }
        )

        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    @property
    def is_configured(self) -> bool:
        """Return ``True`` when the Notion credentials are set."""

        return bool(self.api_key and self.database_id)

    def publish_feeds(self, feeds: List[Dict]) -> bool:
        """Publish the provided feeds to a Notion database page."""

        if not self.is_configured:
            logger.info("Notion integration is not configured. Skipping publish step.")
            return False

        page_title = self._build_page_title()
        properties = self._build_page_properties(page_title)
        children = self._build_children_blocks(feeds)

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
            "children": children,
        }

        try:
            response = self.session.post(self.NOTION_API_URL, json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Successfully published YouTube feeds to Notion.")
            return True
        except requests.HTTPError as error:
            status = error.response.status_code if error.response else "unknown"
            detail = error.response.text if error.response else str(error)
            logger.error(
                "Notion API returned an error (status %s): %s", status, detail
            )
        except requests.RequestException as error:
            logger.error("Network error communicating with Notion API: %s", error)

        return False

    def _build_page_title(self) -> str:
        """Generate the Notion page title based on configuration and time."""

        now = datetime.now(self.timezone)
        date_stamp = now.strftime("%Y-%m-%d")
        return f"{self.page_title_prefix} - {date_stamp}"

    def _build_page_properties(self, page_title: str) -> Dict:
        """Assemble Notion page properties payload."""

        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": page_title,
                        }
                    }
                ]
            }
        }

        if self.date_property_name:
            properties[self.date_property_name] = {
                "date": {"start": datetime.now(self.timezone).isoformat()}
            }

        return properties

    def _build_children_blocks(self, feeds: List[Dict]) -> List[Dict]:
        """Create the Notion block structure for feed content."""

        blocks: List[Dict] = []

        for feed in feeds:
            channel_title = feed.get("channel_title", "Unknown Channel")
            videos = feed.get("videos", [])

            if not videos:
                continue

            blocks.append(
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": channel_title[:2000]},
                            }
                        ]
                    },
                }
            )

            for video in videos:
                title = video.get("title") or "Untitled video"
                summary = self._generate_summary(video.get("description", ""))
                video_id = video.get("video_id")
                watch_url = self._build_watch_url(video, video_id)
                preview_url = self._build_preview_url(video, video_id)

                blocks.extend(
                    [
                        {
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": title[:2000],
                                            "link": {"url": watch_url} if watch_url else None,
                                        },
                                    }
                                ]
                            },
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"Channel: {channel_title}"[:2000],
                                        },
                                    }
                                ]
                            },
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"Summary: {summary}"[:2000],
                                        },
                                    }
                                ]
                            },
                        },
                    ]
                )

                if preview_url:
                    blocks.append(
                        {
                            "type": "video",
                            "video": {
                                "type": "external",
                                "external": {"url": preview_url},
                            },
                        }
                    )
                    blocks.append(
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Preview link",
                                            "link": {"url": preview_url},
                                        },
                                    }
                                ]
                            },
                        }
                    )

                if watch_url:
                    blocks.append(
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Open in YouTube app",
                                            "link": {"url": watch_url},
                                        },
                                    }
                                ]
                            },
                        }
                    )

                blocks.append({"type": "divider", "divider": {}})

        if blocks and blocks[-1].get("type") == "divider":
            blocks.pop()

        if not blocks:
            blocks.append(
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "No videos were fetched for this period.",
                                },
                            }
                        ]
                    },
                }
            )

        return blocks

    def _generate_summary(self, description: str, max_words: int = 200) -> str:
        """Generate a clean summary limited to the desired number of words."""

        if not description:
            return "Not available."

        text = unescape(description)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return "Not available."

        words = text.split()
        if len(words) <= max_words:
            return text

        truncated = " ".join(words[:max_words])
        return f"{truncated}..."

    def _build_preview_url(self, video: Dict, video_id: str | None) -> str:
        """Return a preview URL suitable for Notion's video block."""

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"

        return video.get("link", "")

    def _build_watch_url(self, video: Dict, video_id: str | None) -> str:
        """Return a link that opens the video in the YouTube app."""

        if video_id:
            return f"https://youtu.be/{video_id}"

        return video.get("link", "")
