import re
import scrapy
import dateparser
from ..items import EventItem
from urllib.parse import urlparse, parse_qs


class IswsaSpyder(scrapy.Spider):
    name = "iwsa"
    start_urls = ["https://iwsa.world/events"]

    def parse(self, response):
        smallrows = response.css(".events-table-row")
        expandedrows = response.css(".events-more-info")

        for i in range(0, len(smallrows) - 1):
            event = EventItem()
            event['name'] = smallrows[i + 1].css('.events-event::text').get()
            event['website'] = smallrows[i + 1].css('.events-link a').attrib['href']

            d = expandedrows[i].xpath('string(div[1]/p[1])').get()
            matches = re.search(r'(\w+ \d+, \d{4})', d)
            event["date_start"] = dateparser.parse(matches[0])

            u = expandedrows[i].css('iframe').attrib['src']
            u = urlparse(u)
            event["location"] = parse_qs(u.query)['q'][0]

            yield event
