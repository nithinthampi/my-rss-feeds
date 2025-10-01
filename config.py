import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for YouTube RSS feeds."""

    # YouTube channels configuration
    YOUTUBE_CHANNELS: List[str] = os.getenv(
        "YOUTUBE_CHANNELS",
        "UCBJycsmduvYEL83R_U4JriQ,UCrqM0Ym_NbK1fqeQG2VIohg",
    ).split(",")

    # Output configuration
    OUTPUT_FILE: str = os.getenv("OUTPUT_FILE", "feeds.json")

    # Timezone configuration (used for timestamping)
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

    # Notion integration configuration
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    NOTION_PAGE_TITLE_PREFIX: str = os.getenv(
        "NOTION_PAGE_TITLE_PREFIX", "Daily YouTube Feed"
    )
    NOTION_DATE_PROPERTY: str = os.getenv("NOTION_DATE_PROPERTY", "")

    @classmethod
    def get_youtube_rss_url(cls, channel_id: str) -> str:
        """Generate YouTube RSS URL for a channel."""
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    @classmethod
    def notion_configured(cls) -> bool:
        """Return True when Notion credentials are available."""
        return bool(cls.NOTION_API_KEY and cls.NOTION_DATABASE_ID)
