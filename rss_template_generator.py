import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
import pytz
import logging
from config import Config

logger = logging.getLogger(__name__)


class RSSTemplateGenerator:
    """Generates clean RSS feed templates for YouTube videos."""

    def __init__(self):
        self.config = Config()

    def generate_rss_feed(self, feeds_data: List[Dict], title: str = "My YouTube Feeds") -> str:
        """Generate a clean RSS feed from YouTube feeds data."""
        try:
            # Create RSS root element
            rss = ET.Element("rss")
            rss.set("version", "2.0")
            rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
            rss.set("xmlns:media", "http://search.yahoo.com/mrss/")

            # Create channel element
            channel = ET.SubElement(rss, "channel")
            
            # Channel metadata
            ET.SubElement(channel, "title").text = title
            ET.SubElement(channel, "description").text = "Curated YouTube feeds with clean summaries"
            ET.SubElement(channel, "link").text = "https://www.youtube.com"
            ET.SubElement(channel, "language").text = "en-us"
            ET.SubElement(channel, "lastBuildDate").text = datetime.now(pytz.UTC).strftime("%a, %d %b %Y %H:%M:%S %Z")
            
            # Add atom:link for self-reference
            atom_link = ET.SubElement(channel, "atom:link")
            atom_link.set("href", "https://www.youtube.com")
            atom_link.set("rel", "self")
            atom_link.set("type", "application/rss+xml")

            # Add items for each video
            for feed in feeds_data:
                channel_title = feed.get("channel_title", "Unknown Channel")
                videos = feed.get("videos", [])
                
                for video in videos:
                    item = self._create_video_item(video, channel_title)
                    channel.append(item)

            # Convert to string
            rough_string = ET.tostring(rss, encoding='unicode')
            
            # Pretty print the XML
            return self._pretty_print_xml(rough_string)

        except Exception as e:
            logger.error(f"Error generating RSS feed: {e}")
            return ""

    def _create_video_item(self, video: Dict, channel_title: str) -> ET.Element:
        """Create an RSS item for a single video."""
        item = ET.Element("item")
        
        # Title
        title_elem = ET.SubElement(item, "title")
        title_elem.text = video.get("title", "Untitled Video")
        
        # Link (YouTube app link)
        link_elem = ET.SubElement(item, "link")
        link_elem.text = self._get_youtube_app_link(video.get("link", ""))
        
        # Description with summary
        description_elem = ET.SubElement(item, "description")
        description_elem.text = self._create_video_description(video, channel_title)
        
        # Author/Channel
        author_elem = ET.SubElement(item, "author")
        author_elem.text = channel_title
        
        # Publication date
        pub_date_elem = ET.SubElement(item, "pubDate")
        pub_date = self._parse_pub_date(video.get("published", ""))
        pub_date_elem.text = pub_date.strftime("%a, %d %b %Y %H:%M:%S %Z") if pub_date else datetime.now(pytz.UTC).strftime("%a, %d %b %Y %H:%M:%S %Z")
        
        # GUID
        guid_elem = ET.SubElement(item, "guid")
        guid_elem.text = video.get("link", "")
        guid_elem.set("isPermaLink", "true")
        
        # Media content (thumbnail)
        if video.get("thumbnail"):
            media_content = ET.SubElement(item, "media:content")
            media_content.set("url", video.get("thumbnail"))
            media_content.set("type", "image/jpeg")
            media_content.set("medium", "image")
        
        # Video ID for reference
        video_id = video.get("video_id", "")
        if video_id:
            video_id_elem = ET.SubElement(item, "videoId")
            video_id_elem.text = video_id
        
        # Preview link (web version)
        preview_link_elem = ET.SubElement(item, "previewLink")
        preview_link_elem.text = video.get("link", "")
        
        return item

    def _create_video_description(self, video: Dict, channel_title: str) -> str:
        """Create a clean description with summary."""
        title = video.get("title", "Untitled Video")
        description = video.get("description", "")
        video_id = video.get("video_id", "")
        
        # Clean up description (remove HTML tags, limit length)
        clean_description = self._clean_description(description)
        summary = self._create_summary(clean_description)
        
        # Create formatted description
        desc_parts = [
            f"<strong>Channel:</strong> {channel_title}",
            f"<strong>Summary:</strong> {summary}",
            f"<strong>Video ID:</strong> {video_id}",
            f"<strong>Original Description:</strong> {clean_description[:500]}{'...' if len(clean_description) > 500 else ''}"
        ]
        
        return "<br/><br/>".join(desc_parts)

    def _clean_description(self, description: str) -> str:
        """Clean HTML tags and extra whitespace from description."""
        import re
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', description)
        
        # Remove extra whitespace and newlines
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

    def _create_summary(self, description: str, max_words: int = 200) -> str:
        """Create a summary of the description under specified word limit."""
        if not description:
            return "No description available."
        
        words = description.split()
        if len(words) <= max_words:
            return description
        
        # Take first max_words and add ellipsis
        summary_words = words[:max_words]
        return " ".join(summary_words) + "..."

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

    def _pretty_print_xml(self, xml_string: str) -> str:
        """Pretty print XML string with proper indentation."""
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_string)
            return dom.toprettyxml(indent="  ")
        except Exception:
            return xml_string

    def save_rss_feed(self, feeds_data: List[Dict], filename: str = "youtube_feeds.rss") -> bool:
        """Generate and save RSS feed to file."""
        try:
            rss_content = self.generate_rss_feed(feeds_data)
            
            if not rss_content:
                logger.error("Failed to generate RSS content")
                return False
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(rss_content)
            
            logger.info(f"RSS feed saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving RSS feed: {e}")
            return False