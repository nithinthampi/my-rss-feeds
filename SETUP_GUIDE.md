# YouTube RSS Feed to Notion Setup Guide

This guide will help you set up the YouTube RSS feed fetcher with Notion integration to automatically send your YouTube feeds to your Notion account daily.

## Features

- **Clean RSS Feed Template**: Generates a clean RSS feed with all required information
- **Video Summaries**: Automatically creates summaries under 200 words
- **Notion Integration**: Sends feeds directly to your Notion database
- **Daily Automation**: Runs automatically every day at 9:00 AM
- **Multiple Output Formats**: JSON, RSS, and Notion pages

## RSS Feed Template Information

Each video in the RSS feed includes:
- **Video Title**: Clean, readable title
- **Author/Channel Name**: The YouTube channel name
- **Short Summary**: Video description summarized to under 200 words
- **Preview Link**: Web link to preview the video
- **YouTube App Link**: Direct link that opens in your YouTube app
- **Thumbnail**: Video thumbnail image
- **Publication Date**: When the video was published

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your settings:

```env
# YouTube Channel IDs (comma-separated)
YOUTUBE_CHANNELS=UCBJycsmduvYEL83R_U4JriQ,UCrqM0Ym_NbK1fqeQG2VIohg

# Output file paths
OUTPUT_FILE=feeds.json
RSS_OUTPUT_FILE=youtube_feeds.rss

# Notion Integration (optional)
NOTION_TOKEN=your_notion_integration_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

### 3. Set Up Notion Integration (Optional)

#### Step 1: Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "YouTube RSS Feeds")
4. Select the workspace where you want to create the database
5. Click "Submit"
6. Copy the "Internal Integration Token" and add it to your `.env` file as `NOTION_TOKEN`

#### Step 2: Create a Notion Database

1. Create a new page in Notion
2. Add a database with the following properties:
   - **Title** (Title) - The video title
   - **Channel** (Text) - The YouTube channel name
   - **Published** (Date) - Publication date
   - **Video ID** (Text) - YouTube video ID
   - **Status** (Select) - Options: "New", "Watched", "Summary"

#### Step 3: Share Database with Integration

1. Open your database page
2. Click "Share" in the top right
3. Click "Invite" and select your integration
4. Copy the database ID from the URL and add it to your `.env` file as `NOTION_DATABASE_ID`

The database ID is the long string in your Notion database URL:
```
https://www.notion.so/your-workspace/DATABASE_ID?v=...
```

### 4. Get YouTube Channel IDs

To find YouTube channel IDs:

1. Go to the YouTube channel
2. View page source (Ctrl+U or Cmd+U)
3. Search for "channelId" - the value after it is your channel ID
4. Or use online tools like [YouTube Channel ID Finder](https://commentpicker.com/youtube-channel-id.php)

### 5. Run the Application

#### One-time run:
```bash
python main.py --once
```

#### Continuous operation (with daily scheduling):
```bash
python main.py
```

## Output Files

The application generates several output files:

1. **feeds.json**: Raw feed data in JSON format
2. **youtube_feeds.rss**: Clean RSS feed that can be imported into RSS readers
3. **Notion Database**: Individual pages for each video (if Notion integration is configured)

## RSS Feed Structure

The generated RSS feed includes:

```xml
<rss version="2.0">
  <channel>
    <title>My YouTube Feeds</title>
    <description>Curated YouTube feeds with clean summaries</description>
    <item>
      <title>Video Title</title>
      <link>https://www.youtube.com/watch?v=VIDEO_ID</link>
      <description>
        <strong>Channel:</strong> Channel Name<br/><br/>
        <strong>Summary:</strong> Video summary under 200 words<br/><br/>
        <strong>Video ID:</strong> VIDEO_ID<br/><br/>
        <strong>Original Description:</strong> Full description...
      </description>
      <author>Channel Name</author>
      <pubDate>Publication Date</pubDate>
      <guid>Video URL</guid>
      <media:content url="thumbnail_url" type="image/jpeg"/>
      <videoId>VIDEO_ID</videoId>
      <previewLink>Web preview link</previewLink>
    </item>
  </channel>
</rss>
```

## Notion Database Structure

Each video creates a page in your Notion database with:

- **Title**: Video title
- **Channel**: YouTube channel name
- **Published**: Publication date
- **Video ID**: YouTube video ID
- **Status**: "New" (default)

The page content includes:
- Video summary (under 200 words)
- Preview link (web version)
- YouTube app link (opens in app)
- Thumbnail image
- Full description

## Scheduling

The application runs daily at 9:00 AM by default. You can modify the schedule in `main.py`:

```python
# Change the time in setup_scheduler() function
schedule.every().day.at("09:00").do(run_feed_fetch)
```

## Troubleshooting

### Common Issues

1. **Notion Integration Not Working**
   - Verify your `NOTION_TOKEN` is correct
   - Ensure the integration has access to your database
   - Check that the database ID is correct

2. **YouTube Feeds Not Fetching**
   - Verify channel IDs are correct
   - Check your internet connection
   - Review the logs for specific error messages

3. **RSS Feed Not Generating**
   - Check file permissions in the output directory
   - Verify the `RSS_OUTPUT_FILE` path is writable

### Logs

The application creates detailed logs in `youtube_feeds.log` and outputs to the console. Check these for troubleshooting information.

## Customization

### Modify Summary Length

Edit the `max_words` parameter in `rss_template_generator.py` and `notion_integration.py`:

```python
def _create_summary(self, description: str, max_words: int = 200):
```

### Change Output Format

Modify the RSS template structure in `rss_template_generator.py` to customize the output format.

### Add More Video Information

Extend the video data structure in `youtube_feed_fetcher.py` to include additional information like view count, duration, etc.

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify your configuration settings
3. Test with a single channel first
4. Ensure all dependencies are installed correctly