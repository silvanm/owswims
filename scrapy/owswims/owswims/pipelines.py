# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from itemadapter import ItemAdapter

from .items import EventItem


class OWSwimsPipeline:
    def _replace_nl(self, s: str) -> str:
        # remove repeated spaces
        s = re.sub(r' +', ' ', s)
        return s.translate(str.maketrans({"\n": "", "\r": ""})).strip()

    def process_item(self, event: EventItem, spider):
        event['location'] = self._replace_nl(event['location'])
        if 'description' in event:
            event['description'] = self._replace_nl(event['description'])
        return event
