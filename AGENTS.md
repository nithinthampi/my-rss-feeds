# Agent Documentation for YouTube RSS Feed Fetcher

This document provides comprehensive information for AI agents to understand, maintain, and enhance this YouTube RSS feed fetching application.

## 🏗️ Project Overview

This is a Python-based RSS feed fetcher specifically designed for YouTube channels. It fetches video metadata from multiple YouTube channels and saves the data in structured JSON format with configurable scheduling.

### Core Purpose
- Fetch RSS feeds from multiple YouTube channels
- Schedule regular updates (default: daily)
- Save structured video data to JSON files
- Deploy to cloud platforms for automated operation

## 📁 Repository Structure

```
my-rss-feeds/
├── main.py                    # Application entry point with scheduler
├── youtube_feed_fetcher.py    # Core RSS fetching logic
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── Dockerfile                # Container configuration
├── railway.json              # Railway deployment config
├── render.yaml               # Render deployment config
├── README.md                 # User documentation
└── agents.md                 # This file (agent documentation)
```

## 🔧 Core Components

### 1. `main.py` - Application Entry Point
**Purpose**: Main orchestrator with scheduling logic
**Key Functions**:
- `main()`: Entry point with CLI argument handling
- `run_feed_fetch()`: Executes single fetch operation
- `setup_scheduler()`: Configures recurring fetch schedule

**CLI Arguments**:
- `--once`: Run single fetch and exit
- No args: Run continuous with scheduler

**Dependencies**: `schedule`, `youtube_feed_fetcher`, `config`

### 2. `youtube_feed_fetcher.py` - Core Logic
**Purpose**: Handles all RSS fetching and data processing
**Key Classes**:
- `YouTubeFeedFetcher`: Main fetcher class

**Key Methods**:
- `fetch_channel_feed(channel_id)`: Fetch single channel
- `fetch_all_feeds()`: Fetch all configured channels
- `save_feeds_to_file(feeds, filename)`: Save to JSON
- `run_fetch()`: Complete fetch-and-save operation

**Data Processing**:
- Extracts video metadata (title, link, description, thumbnail)
- Handles RSS parsing errors (`bozo` flag checking)
- Generates structured JSON output

### 3. `config.py` - Configuration Management
**Purpose**: Centralized configuration using environment variables
**Key Properties**:
- `YOUTUBE_CHANNELS`: List of channel IDs
- `OUTPUT_FILE`: JSON output filename
- `UPDATE_FREQUENCY`: Hours between updates
- `TIMEZONE`: Timezone for timestamps

**Helper Methods**:
- `get_youtube_rss_url(channel_id)`: Generate RSS URLs

## 🔄 Data Flow

1. **Configuration Load**: Environment variables loaded via `config.py`
2. **Channel Processing**: Each channel ID converted to YouTube RSS URL
3. **RSS Fetching**: HTTP requests to YouTube RSS endpoints
4. **Data Parsing**: feedparser processes XML into structured data
5. **Error Handling**: Bozo flag checking for parsing issues
6. **Data Transformation**: Raw feed data converted to standardized format
7. **JSON Output**: Structured data saved to file with metadata

## 📊 Data Schema

### Input (Environment Variables)
```python
YOUTUBE_CHANNELS: str  # Comma-separated channel IDs
OUTPUT_FILE: str       # JSON output filename
UPDATE_FREQUENCY: int  # Hours between updates
TIMEZONE: str          # Timezone identifier
```

### Output (JSON Structure)
```json
{
  "fetched_at": "ISO timestamp",
  "total_channels": int,
  "feeds": [
    {
      "channel_id": "string",
      "channel_title": "string", 
      "channel_link": "string",
      "last_updated": "ISO timestamp",
      "videos": [
        {
          "title": "string",
          "link": "string",
          "published": "RSS date string",
          "description": "string",
          "video_id": "string",
          "thumbnail": "string"
        }
      ]
    }
  ]
}
```

## 🚀 Deployment Architecture

### Supported Platforms
1. **Railway**: Primary recommendation (500h free + $5 credit)
2. **Render**: Good alternative (750h free, sleeps after inactivity)
3. **Fly.io**: Docker-based deployment (3 free VMs)
4. **GitHub Actions**: Cron-style scheduling (2000 min free)

### Deployment Files
- `Dockerfile`: Container configuration for Docker-based platforms
- `railway.json`: Railway-specific deployment settings
- `render.yaml`: Render-specific deployment configuration

## 🛠️ Development Guidelines

### Adding New Features

#### 1. New Data Fields
**Location**: `youtube_feed_fetcher.py` → `_process_videos()`
**Process**:
- Add extraction logic in `_process_videos()`
- Update JSON schema documentation
- Test with sample feeds

#### 2. New Configuration Options
**Location**: `config.py`
**Process**:
- Add new property with `os.getenv()` and default
- Update `.env.example` with new variable
- Update `agents.md` documentation

#### 3. New Output Formats
**Location**: `youtube_feed_fetcher.py` → `save_feeds_to_file()`
**Process**:
- Add format detection logic
- Implement new serialization method
- Update configuration options

### Error Handling Patterns

#### Network Errors
```python
try:
    response = self.session.get(rss_url, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Network error: {e}")
    return None
```

#### RSS Parsing Errors
```python
feed = feedparser.parse(response.content)
if feed.bozo:
    logger.warning(f"Feed parsing issues: {feed.bozo_exception}")
```

#### Data Processing Errors
```python
try:
    video_data = {...}
    videos.append(video_data)
except Exception as e:
    logger.warning(f"Error processing entry: {e}")
    continue  # Skip problematic entries
```

### Logging Standards

#### Log Levels
- **INFO**: Normal operations, successful fetches
- **WARNING**: Non-critical issues (bozo feeds, skipped entries)
- **ERROR**: Failed operations, network issues

#### Log Format
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_feeds.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

## 🔍 Testing Strategies

### Manual Testing
```bash
# Test single fetch
python main.py --once

# Test configuration loading
python -c "from config import Config; print(Config.YOUTUBE_CHANNELS)"

# Test specific channel
python -c "from youtube_feed_fetcher import YouTubeFeedFetcher; f = YouTubeFeedFetcher(); print(f.fetch_channel_feed('UCBJycsmduvYEL83R_U4JriQ'))"
```

### Common Test Cases
1. **Valid channels**: Test with known public YouTube channels
2. **Invalid channels**: Test with non-existent channel IDs
3. **Network failures**: Test with invalid URLs
4. **Malformed feeds**: Test with feeds that trigger `bozo=True`
5. **File permissions**: Test JSON file writing

## 🐛 Common Issues & Solutions

### Issue: "No feeds were successfully fetched"
**Causes**:
- Invalid channel IDs
- Network connectivity issues
- YouTube API changes
- Rate limiting

**Debug Steps**:
1. Check channel IDs are valid
2. Test network connectivity
3. Verify YouTube RSS URLs manually
4. Check logs for specific error messages

### Issue: "Feed parsing issues" (bozo=True)
**Causes**:
- Malformed XML in RSS feed
- Encoding issues
- Partial downloads

**Handling**:
- Log warning but continue processing
- feedparser often extracts usable data despite bozo=True
- Monitor for recurring issues

### Issue: Permission errors writing JSON
**Causes**:
- Insufficient file permissions
- Directory doesn't exist
- Disk space issues

**Solutions**:
- Check output directory permissions
- Ensure sufficient disk space
- Use absolute paths for output files

## 🔄 Maintenance Tasks

### Regular Updates
1. **Dependencies**: Update `requirements.txt` versions
2. **Python version**: Test with newer Python versions
3. **YouTube changes**: Monitor for RSS format changes
4. **Log rotation**: Implement log file rotation for long-running instances

### Monitoring
1. **Success rates**: Track successful vs failed fetches
2. **Performance**: Monitor fetch times and resource usage
3. **Data quality**: Validate JSON output structure
4. **Error patterns**: Analyze recurring error types

## 📝 Code Style Guidelines

### Python Standards
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Prefer descriptive variable names
- Include docstrings for public methods

### Error Handling
- Use specific exception types
- Log errors with context
- Fail gracefully where possible
- Continue processing despite individual failures

### Configuration
- Use environment variables for all configurable options
- Provide sensible defaults
- Validate configuration on startup
- Document all configuration options

## 🔗 External Dependencies

### Core Libraries
- **feedparser**: RSS/XML parsing
- **requests**: HTTP requests
- **python-dotenv**: Environment variable loading
- **schedule**: Task scheduling
- **pytz**: Timezone handling

### Version Compatibility
- **Python**: 3.9+ (tested on 3.11)
- **feedparser**: 6.0.10+
- **requests**: 2.31.0+

## 🚨 Breaking Changes

### Potential Breaking Changes
1. **YouTube RSS format changes**: May require feedparser updates
2. **Python version upgrades**: May require dependency updates
3. **Cloud platform changes**: May require deployment config updates

### Migration Strategies
1. **Version pinning**: Pin dependency versions in requirements.txt
2. **Graceful degradation**: Handle missing fields in RSS feeds
3. **Backward compatibility**: Maintain support for older data formats

## 📋 Agent Checklist

When making changes to this repository:

### Before Changes
- [ ] Understand the component you're modifying
- [ ] Check existing error handling patterns
- [ ] Review configuration options
- [ ] Consider impact on cloud deployments

### During Changes
- [ ] Follow existing code style
- [ ] Add appropriate error handling
- [ ] Include logging statements
- [ ] Update documentation if needed

### After Changes
- [ ] Test with `python main.py --once`
- [ ] Verify JSON output format
- [ ] Check logs for errors/warnings
- [ ] Update this documentation if needed

### For New Features
- [ ] Add configuration options to `config.py`
- [ ] Update `.env.example` file
- [ ] Add deployment configs if needed
- [ ] Update README.md user documentation
- [ ] Update this agents.md file

This documentation should enable any AI agent to understand, maintain, and enhance this YouTube RSS feed fetching application effectively.
