import scrapy
from ..items import PlayerStatsItem


class TestSpider(scrapy.Spider):
    name = 'test_spider'
    start_urls = [
        'https://httpbin.org/html',  # Simple test page
        'https://www.basketball-bund.net/',  # Basketball site
    ]
    
    def parse(self, response):
        self.logger.info(f"Successfully fetched: {response.url}")
        self.logger.info(f"Status: {response.status}")
        self.logger.info(f"Content length: {len(response.body)}")
        
        # Try to find any text content
        title = response.css('title::text').get()
        if title:
            self.logger.info(f"Page title: {title}")
        
        # Look for any links
        links = response.css('a::attr(href)').getall()[:5]  # First 5 links
        for link in links:
            self.logger.info(f"Found link: {link}")
            
        # Create a simple test item
        item = PlayerStatsItem()
        item['name'] = f'Test player from {response.url}'
        item['source_url'] = response.url
        yield item
