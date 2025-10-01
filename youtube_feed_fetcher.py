import feedparser
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pytz
from config import Config
from notion_publisher import NotionPublisher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeFeedFetcher:
    """Fetches and processes YouTube RSS feeds."""

    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "YouTube RSS Feed Fetcher/1.0"})
        self.notion_publisher = NotionPublisher(self.config)

    def fetch_channel_feed(self, channel_id: str) -> Optional[Dict]:
        """Fetch RSS feed for a single YouTube channel."""
        try:
            rss_url = self.config.get_youtube_rss_url(channel_id)
            logger.info(f"Fetching feed for channel: {channel_id}")

            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo:
                logger.warning(
                    f"Feed parsing issues for channel {channel_id}: {feed.bozo_exception}"
                )

            return {
                "channel_id": channel_id,
                "channel_title": feed.feed.get("title", "Unknown Channel"),
                "channel_link": feed.feed.get("link", ""),
                "last_updated": datetime.now(pytz.UTC).isoformat(),
                "videos": self._process_videos(feed.entries),
            }

        except requests.RequestException as e:
            logger.error(f"Network error fetching feed for {channel_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing feed for {channel_id}: {e}")
            return None

    def _process_videos(self, entries: List) -> List[Dict]:
        """Process video entries from RSS feed."""
        videos = []

        for entry in entries:
            try:
                video_data = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "description": entry.get("summary", ""),
                    "video_id": self._extract_video_id(entry.get("link", "")),
                    "thumbnail": self._extract_thumbnail(entry),
                }
                videos.append(video_data)
            except Exception as e:
                logger.warning(f"Error processing video entry: {e}")
                continue

        return videos

    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL."""
        try:
            return video_url.split("v=")[1].split("&")[0]
        except (IndexError, AttributeError):
            return ""

    def _extract_thumbnail(self, entry) -> str:
        """Extract thumbnail URL from video entry."""
        try:
            # Try to get thumbnail from media content
            if hasattr(entry, "media_thumbnail"):
                return entry.media_thumbnail[0]["url"]

            # Fallback to YouTube thumbnail URL using video ID
            video_id = self._extract_video_id(entry.get("link", ""))
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

            return ""
        except Exception:
            return ""

    def fetch_all_feeds(self) -> List[Dict]:
        """Fetch feeds for all configured channels."""
        all_feeds = []

        for channel_id in self.config.YOUTUBE_CHANNELS:
            channel_id = channel_id.strip()
            if not channel_id:
                continue

            feed_data = self.fetch_channel_feed(channel_id)
            if feed_data:
                all_feeds.append(feed_data)
            else:
                logger.error(f"Failed to fetch feed for channel: {channel_id}")

        return all_feeds

    def save_feeds_to_file(self, feeds: List[Dict], filename: str = None) -> bool:
        """Save feeds data to JSON file."""
        try:
            filename = filename or self.config.OUTPUT_FILE
            output_data = {
                "fetched_at": datetime.now(pytz.UTC).isoformat(),
                "total_channels": len(feeds),
                "feeds": feeds,
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Feeds saved to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving feeds to file: {e}")
            return False

    def run_fetch(self) -> bool:
        """Main method to fetch all feeds and save to file."""
        logger.info("Starting YouTube RSS feed fetch...")

        feeds = self.fetch_all_feeds()

        if not feeds:
            logger.error("No feeds were successfully fetched")
            return False

        success = self.save_feeds_to_file(feeds)

        notion_success = True
        if self.notion_publisher.is_configured:
            notion_success = self.notion_publisher.publish_feeds(feeds)
            if notion_success:
                logger.info("Feeds were sent to Notion successfully")
            else:
                logger.error("Failed to publish feeds to Notion")
        else:
            logger.info("Notion integration not configured. Skipping Notion publish.")

        if success:
            total_videos = sum(len(feed["videos"]) for feed in feeds)
            logger.info(
                f"Successfully fetched {len(feeds)} channels with {total_videos} total videos"
            )

        return success and notion_success
