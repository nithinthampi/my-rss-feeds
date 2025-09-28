#!/usr/bin/env python3
"""
YouTube RSS Feed Fetcher
Main application entry point for fetching YouTube RSS feeds.
"""

import sys
import logging
import schedule
import time
from datetime import datetime
import pytz
from youtube_feed_fetcher import YouTubeFeedFetcher
from rss_template_generator import RSSTemplateGenerator
from notion_integration import NotionIntegration
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_feeds.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_feed_fetch():
    """Run a single feed fetch operation."""
    logger.info("=" * 50)
    logger.info("Starting scheduled YouTube RSS feed fetch")
    
    try:
        # Initialize components
        fetcher = YouTubeFeedFetcher()
        rss_generator = RSSTemplateGenerator()
        notion_integration = NotionIntegration()
        config = Config()
        
        # Fetch YouTube feeds
        logger.info("Fetching YouTube feeds...")
        feeds = fetcher.fetch_all_feeds()
        
        if not feeds:
            logger.error("No feeds were successfully fetched")
            return False
        
        # Save to JSON file
        success = fetcher.save_feeds_to_file(feeds)
        if not success:
            logger.error("Failed to save feeds to JSON file")
            return False
        
        # Generate RSS feed
        logger.info("Generating RSS feed...")
        rss_success = rss_generator.save_rss_feed(feeds, config.RSS_OUTPUT_FILE)
        if rss_success:
            logger.info(f"RSS feed saved to {config.RSS_OUTPUT_FILE}")
        else:
            logger.warning("Failed to generate RSS feed")
        
        # Send to Notion (if configured)
        if config.NOTION_TOKEN and config.NOTION_DATABASE_ID:
            logger.info("Sending feeds to Notion...")
            notion_success = notion_integration.send_feeds_to_notion(feeds)
            if notion_success:
                logger.info("Successfully sent feeds to Notion")
                
                # Create daily summary
                summary_success = notion_integration.create_daily_summary_page(feeds)
                if summary_success:
                    logger.info("Created daily summary page in Notion")
            else:
                logger.warning("Failed to send feeds to Notion")
        else:
            logger.info("Notion integration not configured (missing NOTION_TOKEN or NOTION_DATABASE_ID)")
        
        # Log summary
        total_videos = sum(len(feed["videos"]) for feed in feeds)
        logger.info(f"Successfully processed {len(feeds)} channels with {total_videos} total videos")
        
        return True
            
    except Exception as e:
        logger.error(f"Unexpected error during feed fetch: {e}")
        return False
    
    logger.info("=" * 50)

def setup_scheduler():
    """Set up the scheduled feed fetching."""
    # Schedule daily fetch at 09:00
    schedule.every().day.at("09:00").do(run_feed_fetch)
    logger.info("Scheduled feed fetch daily at 09:00")
    
    # Run initial fetch
    logger.info("Running initial feed fetch...")
    run_feed_fetch()

def main():
    """Main application entry point."""
    logger.info("YouTube RSS Feed Fetcher starting...")
    
    # Check if running in one-time mode
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        logger.info("Running in one-time mode")
        run_feed_fetch()
        return
    
    # Set up scheduler for continuous operation
    setup_scheduler()
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
