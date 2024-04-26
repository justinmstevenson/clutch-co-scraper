# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import re

class BusinessItem(scrapy.Item):
    id = scrapy.Field()
    data_type = scrapy.Field()
    data_title = scrapy.Field()
    data_is_paid = scrapy.Field()
    profile_link = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field(input_processor=MapCompose(lambda x: re.sub(r'[^0-9]', '', x)))
    min_project_size = scrapy.Field()
    avg_hourly_rate = scrapy.Field()
    employees = scrapy.Field()
    location = scrapy.Field()
    service_focus = scrapy.Field()
    summary = scrapy.Field()
    website = scrapy.Field(input_processor=MapCompose(lambda x: re.sub(r'\?utm_source.*$', '', x)))
    url = scrapy.Field(output_processor=TakeFirst()) 
    
