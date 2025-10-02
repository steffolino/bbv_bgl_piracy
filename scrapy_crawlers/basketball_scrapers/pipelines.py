# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from datetime import datetime
from itemadapter import ItemAdapter


class JsonWriterPipeline:
    """Pipeline that writes scraped items to JSON file"""
    
    def open_spider(self, spider):
        self.file = open('scraped_data.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
            
        # Add timestamp
        adapter['scraped_at'] = datetime.now().isoformat()
        
        line = json.dumps(dict(adapter), ensure_ascii=False, indent=2)
        self.file.write(line)
        return item


class DatabasePipeline:
    """Pipeline that saves items to database (placeholder for now)"""
    
    def open_spider(self, spider):
        spider.logger.info("Database pipeline opened")
        # TODO: Initialize database connection here
        
    def close_spider(self, spider):
        spider.logger.info("Database pipeline closed")
        # TODO: Close database connection here
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # TODO: Save item to database
        spider.logger.info(f"Processing item: {adapter.get('name', 'Unknown')}")
        
        return item


class ValidationPipeline:
    """Pipeline that validates scraped data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Basic validation
        if not adapter.get('name'):
            spider.logger.warning(f"Item missing name: {dict(adapter)}")
            
        # Add more validation rules as needed
        
        return item
