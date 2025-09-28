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
        fetcher = YouTubeFeedFetcher()
        success = fetcher.run_fetch()
        
        if success:
            logger.info("Feed fetch completed successfully")
        else:
            logger.error("Feed fetch failed")
            
    except Exception as e:
        logger.error(f"Unexpected error during feed fetch: {e}")
    
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
