# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EventItem(scrapy.Item):
    name = scrapy.Field()
    location = scrapy.Field()
    address = scrapy.Field()
    races = scrapy.Field()
    wetsuit = scrapy.Field()
    water_type = scrapy.Field()
    date_start = scrapy.Field()
    date_end = scrapy.Field()
    description = scrapy.Field()
    website = scrapy.Field()
