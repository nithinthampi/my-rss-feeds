import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for YouTube RSS feeds."""
    
    # YouTube channels configuration
    YOUTUBE_CHANNELS: List[str] = os.getenv(
        'YOUTUBE_CHANNELS', 
        'UCBJycsmduvYEL83R_U4JriQ,UCrqM0Ym_NbK1fqeQG2VIohg'
    ).split(',')
    
    # Output configuration
    OUTPUT_FILE: str = os.getenv('OUTPUT_FILE', 'feeds.json')
    RSS_OUTPUT_FILE: str = os.getenv('RSS_OUTPUT_FILE', 'youtube_feeds.rss')
    
    # Notion configuration
    NOTION_TOKEN: str = os.getenv('NOTION_TOKEN', '')
    NOTION_DATABASE_ID: str = os.getenv('NOTION_DATABASE_ID', '')
    
    @classmethod
    def get_youtube_rss_url(cls, channel_id: str) -> str:
        """Generate YouTube RSS URL for a channel."""
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
