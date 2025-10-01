# YouTube RSS Feed Fetcher

A Python application that fetches RSS feeds from YouTube channels and saves them to a JSON file. Perfect for keeping track of your favorite YouTube channels' latest videos.

## Features

- 🎥 Fetch RSS feeds from multiple YouTube channels
- 📅 Scheduled daily updates (9 AM UTC)
- 💾 Save feeds to JSON format
- 🗒️ Publish a clean daily digest directly to Notion
- ⚙️ Simple configuration via environment variables
- 📝 Comprehensive logging
- 🖥️ Designed for local usage

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd my-rss-feeds

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your YouTube channel IDs and (optionally) Notion credentials:

```env
# YouTube Channel IDs (comma-separated)
YOUTUBE_CHANNELS=UCBJycsmduvYEL83R_U4JriQ,UCrqM0Ym_NbK1fqeQG2VIohg

# Output file path
OUTPUT_FILE=feeds.json

# Optional timezone for timestamps
TIMEZONE=UTC

# Notion (required if you want pages created automatically)
NOTION_API_KEY=secret_notion_token
NOTION_DATABASE_ID=your_database_id
NOTION_PAGE_TITLE_PREFIX=Daily YouTube Feed
# Optional: if your database has a date property you want populated
NOTION_DATE_PROPERTY=Date
```

### 3. Finding YouTube Channel IDs

To get a YouTube channel ID:

1. Go to the YouTube channel page
2. View page source (Ctrl+U)
3. Search for `"channelId":"` - the ID follows this string
4. Or use online tools like [commentpicker.com/youtube-channel-id.php](https://commentpicker.com/youtube-channel-id.php)


## Output Format

The application generates a JSON file with the following structure:

```json
{
  "fetched_at": "2024-01-15T09:00:00+00:00",
  "total_channels": 2,
  "feeds": [
    {
      "channel_id": "UCBJycsmduvYEL83R_U4JriQ",
      "channel_title": "Channel Name",
      "channel_link": "https://youtube.com/channel/...",
      "last_updated": "2024-01-15T09:00:00+00:00",
      "videos": [
        {
          "title": "Video Title",
          "link": "https://youtube.com/watch?v=...",
          "published": "Mon, 15 Jan 2024 08:00:00 +0000",
          "description": "Video description...",
          "video_id": "dQw4w9WgXcQ",
          "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
        }
      ]
    }
  ]
}
```

## Local Usage

This application is designed to run locally on your machine. You can run it in two modes:

### One-time Fetch
Perfect for testing or getting feeds immediately:
```bash
python main.py --once
```

### Continuous Operation
Runs continuously with daily scheduling:
```bash
python main.py
```
The application will fetch feeds daily at 9:00 AM UTC and continue running until you stop it with Ctrl+C.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `YOUTUBE_CHANNELS` | Comma-separated channel IDs | Required |
| `OUTPUT_FILE` | JSON output filename | `feeds.json` |
| `TIMEZONE` | Olson timezone name used for timestamps | `UTC` |
| `NOTION_API_KEY` | Notion integration secret | Required for Notion |
| `NOTION_DATABASE_ID` | Target Notion database ID | Required for Notion |
| `NOTION_PAGE_TITLE_PREFIX` | Prefix for generated page titles | `Daily YouTube Feed` |
| `NOTION_DATE_PROPERTY` | Name of Notion date property to populate | _empty_ |

**Note**: The application runs on a fixed daily schedule (9 AM UTC). When Notion
credentials are provided, a new page is created in the configured database with
the latest videos, including title, author, a summary under 200 words, a video
preview embed, and a direct link that opens in the YouTube app.

## Logging

The application creates detailed logs in `youtube_feeds.log` and outputs to console. Log levels include:

- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failed operations

## Troubleshooting

### Common Issues

1. **"No feeds were successfully fetched"**
   - Check if channel IDs are correct
   - Verify internet connection
   - Check if channels are public

2. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Permission errors**
   - Check file write permissions
   - Ensure output directory exists

### Getting Help

- Check the logs in `youtube_feeds.log`
- Verify your `.env` configuration
- Test with `python main.py --once` first

## License

MIT License - feel free to use and modify as needed!
