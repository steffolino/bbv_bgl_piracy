# Scrapy settings for basketball_scrapers project

BOT_NAME = 'basketball_scrapers'

SPIDER_MODULES = ['basketball_scrapers.spiders']
NEWSPIDER_MODULE = 'basketball_scrapers.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Set to True if you want to respect robots.txt

# Configure delays for requests (be respectful!)
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY_RANGE = 0.5

# Configure user agent
USER_AGENT = 'basketball_scrapers (+https://github.com/steffolino/bbv_bgl_piracy)'

# Configure pipelines
ITEM_PIPELINES = {
    'basketball_scrapers.pipelines.DatabasePipeline': 300,
    'basketball_scrapers.crawl_logger.CrawlLoggerPipeline': 100,
}

# Configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'basketball_scrapers.crawl_logger.EnhancedRequestMiddleware': 543,
}

# Enhanced logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Enable enhanced crawl logging
CRAWL_LOGGING_ENABLED = True
CRAWL_LOGGING_DB_PATH = 'crawl_logs.db'

# AutoThrottle settings for better performance monitoring
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = True

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Configure logging
LOG_LEVEL = 'INFO'

# Database configuration (for pipeline)
DATABASE_URL = 'sqlite:///basketball_stats.db'  # Change this to your database URL

# Request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
