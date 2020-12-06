import logging
import re
from typing import List, Tuple

import scrapy
import dateparser
from ..items import EventItem


class SchwimmkalenderSpyder(scrapy.Spider):
    name = "schwimmkalender"
    start_urls = ["http://schwimmkalender.de/index.php/freiwasser"]

    def parse(self, response):
        for src in response.css(".eventlist li"):
            event = EventItem()
            event["date_start"] = dateparser.parse(
                src.css(".jem-event-date > meta").attrib["content"]
            )
            titlecol = src.css(".jem-event-title")
            detail_url = response.urljoin(titlecol.css("a").attrib["href"])
            titlestr = titlecol.css("a::text").get()

            event["name"], city, distances = self.parse_titlestr(titlestr)
            location2 = (
                src.xpath(
                    'string(div[@class="jem-event-info-small jem-event-venue"])'
                )
                .get()
                .strip()
            )
            logging.warning(f"{city}, {location2}")

            event["location"] = (city + ", " if city else "") + location2
            event["races"] = distances

            yield scrapy.Request(
                detail_url, callback=self.parse_event, cb_kwargs=dict(event=event)
            )

    def parse_event(self, response, event: EventItem):
        event["website"] = response.css(".event_desc a").attrib["href"]
        yield event

    def parse_titlestr(self, s: str) -> Tuple[str, str, list]:
        m = re.search(r"([^,]*)(?:, (.*))? \((.*)\)", s)
        title = m[1] if m[1] else None
        city = m[2] if m[2] else None
        distancestr = m[3] if m[3] else None
        distances = []

        if distancestr:
            distances = re.findall(r"\b(?:([\d,]+)k?)\b", distancestr)
            distances = [float(d.replace(",", ".")) for d in distances]

        return title, city, distances

        # (([\d, ]+k?)[;+]?) +
        # ([^,]*)(, .*)? \((.*)\)
