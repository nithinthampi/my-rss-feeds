import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pytz
from config import Config

logger = logging.getLogger(__name__)


class NotionIntegration:
    """Integrates with Notion API to send YouTube feeds."""

    def __init__(self):
        self.config = Config()
        self.notion_token = self.config.NOTION_TOKEN
        self.notion_database_id = self.config.NOTION_DATABASE_ID
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_database_page(self, video_data: Dict, channel_title: str) -> bool:
        """Create a new page in Notion database for a video."""
        try:
            url = "https://api.notion.com/v1/pages"
            
            # Prepare page data
            page_data = {
                "parent": {"database_id": self.notion_database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": video_data.get("title", "Untitled Video")
                                }
                            }
                        ]
                    },
                    "Channel": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": channel_title
                                }
                            }
                        ]
                    },
                    "Published": {
                        "date": {
                            "start": self._parse_pub_date(video_data.get("published", "")).strftime("%Y-%m-%d")
                        }
                    },
                    "Video ID": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": video_data.get("video_id", "")
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": "New"
                        }
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "Video Summary"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": self._create_summary(video_data.get("description", ""))
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "Links"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "Preview Link: ",
                                        "annotations": {
                                            "bold": True
                                        }
                                    }
                                },
                                {
                                    "text": {
                                        "content": video_data.get("link", ""),
                                        "link": {
                                            "url": video_data.get("link", "")
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "YouTube App Link: ",
                                        "annotations": {
                                            "bold": True
                                        }
                                    }
                                },
                                {
                                    "text": {
                                        "content": self._get_youtube_app_link(video_data.get("link", "")),
                                        "link": {
                                            "url": self._get_youtube_app_link(video_data.get("link", ""))
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

            # Add thumbnail if available
            if video_data.get("thumbnail"):
                page_data["children"].append({
                    "object": "block",
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": video_data.get("thumbnail")
                        }
                    }
                })

            # Add full description if available
            if video_data.get("description"):
                page_data["children"].extend([
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "Full Description"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": self._clean_description(video_data.get("description", ""))[:2000]
                                    }
                                }
                            ]
                        }
                    }
                ])

            response = requests.post(url, headers=self.headers, json=page_data)
            response.raise_for_status()
            
            logger.info(f"Created Notion page for video: {video_data.get('title', 'Unknown')}")
            return True

        except requests.RequestException as e:
            logger.error(f"Error creating Notion page: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating Notion page: {e}")
            return False

    def send_feeds_to_notion(self, feeds_data: List[Dict]) -> bool:
        """Send all feeds to Notion database."""
        try:
            total_videos = 0
            successful_pages = 0

            for feed in feeds_data:
                channel_title = feed.get("channel_title", "Unknown Channel")
                videos = feed.get("videos", [])
                
                logger.info(f"Processing {len(videos)} videos from {channel_title}")
                
                for video in videos:
                    total_videos += 1
                    if self.create_database_page(video, channel_title):
                        successful_pages += 1

            logger.info(f"Successfully created {successful_pages}/{total_videos} Notion pages")
            return successful_pages > 0

        except Exception as e:
            logger.error(f"Error sending feeds to Notion: {e}")
            return False

    def create_daily_summary_page(self, feeds_data: List[Dict]) -> bool:
        """Create a daily summary page in Notion."""
        try:
            url = "https://api.notion.com/v1/pages"
            
            today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
            total_videos = sum(len(feed.get("videos", [])) for feed in feeds_data)
            total_channels = len(feeds_data)
            
            page_data = {
                "parent": {"database_id": self.notion_database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": f"Daily YouTube Feed Summary - {today}"
                                }
                            }
                        ]
                    },
                    "Channel": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "Daily Summary"
                                }
                            }
                        ]
                    },
                    "Published": {
                        "date": {
                            "start": today
                        }
                    },
                    "Status": {
                        "select": {
                            "name": "Summary"
                        }
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "heading_1",
                        "heading_1": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": f"YouTube Feed Summary - {today}"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": f"Total Channels: {total_channels}\nTotal Videos: {total_videos}\nFetched at: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": "Channel Breakdown"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

            # Add channel breakdown
            for feed in feeds_data:
                channel_title = feed.get("channel_title", "Unknown Channel")
                video_count = len(feed.get("videos", []))
                
                page_data["children"].append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": f"{channel_title}: {video_count} videos"
                                }
                            }
                        ]
                    }
                })

            response = requests.post(url, headers=self.headers, json=page_data)
            response.raise_for_status()
            
            logger.info(f"Created daily summary page for {today}")
            return True

        except Exception as e:
            logger.error(f"Error creating daily summary page: {e}")
            return False

    def _create_summary(self, description: str, max_words: int = 200) -> str:
        """Create a summary of the description under specified word limit."""
        if not description:
            return "No description available."
        
        clean_desc = self._clean_description(description)
        words = clean_desc.split()
        
        if len(words) <= max_words:
            return clean_desc
        
        # Take first max_words and add ellipsis
        summary_words = words[:max_words]
        return " ".join(summary_words) + "..."

    def _clean_description(self, description: str) -> str:
        """Clean HTML tags and extra whitespace from description."""
        import re
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', description)
        
        # Remove extra whitespace and newlines
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

    def _get_youtube_app_link(self, web_link: str) -> str:
        """Convert web YouTube link to app link."""
        if not web_link:
            return ""
        
        # Extract video ID
        video_id = self._extract_video_id(web_link)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        
        return web_link

    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL."""
        try:
            return video_url.split("v=")[1].split("&")[0]
        except (IndexError, AttributeError):
            return ""

    def _parse_pub_date(self, date_str: str) -> datetime:
        """Parse publication date string to datetime object."""
        try:
            # Try common date formats
            formats = [
                "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            return datetime.now(pytz.UTC)
            
        except Exception:
            return datetime.now(pytz.UTC)