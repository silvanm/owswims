import re
from typing import List

import scrapy
import dateparser
from ..items import EventItem


class QuotesSpider(scrapy.Spider):
    name = "outdoorswimmer"
    start_urls = ["https://outdoorswimmer.com/find/events"]

    def parse(self, response):
        for eventstr in response.css(".c-content__column .c-items__item"):
            url = response.urljoin(str(eventstr.css('a::attr("href")').get()))
            badges = eventstr.css(".c-badges__badge .c-badge")

            event = EventItem()

            event["wetsuit"] = badges[0].attrib["data-tooltip"]
            event["water_type"] = badges[1].attrib["data-tooltip"]

            yield scrapy.Request(
                url, callback=self.parse_event, cb_kwargs=dict(event=event)
            )

        next_page = response.xpath("//a[contains(.//text(), 'Next Page')]")
        if next_page:
            url_next_page = next_page[0].attrib["href"]
            if url_next_page is not None:
                url_next_page = response.urljoin(url_next_page)
                yield scrapy.Request(url_next_page, callback=self.parse)

    def parse_distances(self, s)->List:
        matches = re.findall(r"(([\d.]+) ?(k?m|miles?)\b)", s)
        result = []
        for m in matches:
            print(m[2])
            if m[2] == 'mile' or m[2] == 'miles':
                factor = 1/1.609
            elif m[2] == 'm':
                factor = 1000
            else:
                factor = 1
            result.append(float(m[1]) / factor)
        return result


    def parse_event(self, response, event: EventItem):

        event["name"] = response.css("h1::text").get()

        subheading = response.css(".c-article .o-subheading::text").get()
        parts = subheading.split(" | ")
        event["date_start"] = dateparser.parse(parts[1])

        description = " ".join(
            response.css(".o-section.o-section--outline p::text").getall()
        )

        # distances
        races = self.parse_distances(description)
        if races:
            event["races"] = races

        # url
        m = re.search(r"\b([a-z0-9-.]*)\.([a-z]{2,10})\b", description)
        if m:
            event["website"] = 'http://' + m[0]

        event["name"] = response.css("h1::text").get()
        event["description"] = description

        location = response.xpath('string(//div[@class="c-content__column c-content__column--1of3"])').get()
        event["location"] = location

        yield event
