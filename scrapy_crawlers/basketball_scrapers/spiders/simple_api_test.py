import scrapy
import json

class SimpleApiTestSpider(scrapy.Spider):
    name = 'simple_api_test'
    allowed_domains = ['basketball-bund.net']
    start_urls = ['https://www.basketball-bund.net/']
    
    def parse(self, response):
        # Test the exact API call with minimal parameters
        yield scrapy.Request(
            url='https://www.basketball-bund.net/rest/wam/data',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "verbandIds": [2],
                "gebietIds": ["5_"]
            }),
            callback=self.parse_api_response
        )
    
    def parse_api_response(self, response):
        """Log the full API response to understand the structure"""
        self.logger.info(f'Status: {response.status}')
        self.logger.info(f'Headers: {dict(response.headers)}')
        self.logger.info(f'Full Response Text:')
        self.logger.info(response.text)
        
        try:
            data = json.loads(response.text)
            self.logger.info(f'JSON Structure:')
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    self.logger.info(f'  {key}: {type(value)} with {len(value) if hasattr(value, "__len__") else "?"} items')
                    if isinstance(value, list) and len(value) > 0:
                        self.logger.info(f'    First item: {value[0]}')
                    elif isinstance(value, dict) and value:
                        self.logger.info(f'    Keys: {list(value.keys())[:5]}')
                else:
                    self.logger.info(f'  {key}: {value}')
        except:
            self.logger.info('Could not parse as JSON')
