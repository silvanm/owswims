import csv
from datetime import date
from typing import Dict, Tuple, List

import requests
from bs4 import BeautifulSoup
import re
import dateparser
from django_countries import countries
from django_countries.fields import Country

from typing import TypedDict


class ImportedEvent(TypedDict):
    date: date
    event: str
    website: str
    location: Tuple[str, Country]
    races: List[float]


class ImportResult(TypedDict):
    parsed_items: List[ImportedEvent]
    failed_items: list


class NotParsableException(Exception):
    not_parsable_part = ""

    def __init__(self, not_parsable_part: str):
        self.not_parsable_part = not_parsable_part


def resolve_country(source: str) -> str:
    """
    Turns 'CIPRIO' into the Country object for Cyprus
    :param source:str
    :return:
    """
    with open("app/data/countries_it.csv", "r") as csvfile:
        countryreader = csv.reader(csvfile, delimiter=",", quotechar='"')
        country_to_iso = {}
        for row in countryreader:
            country_to_iso[row[1].lower()] = row[2]
    try:
        return country_to_iso[source.lower()].upper()
    except KeyError:
        raise NotParsableException(not_parsable_part=source)


def resolve_location_string(source: str) -> (str, str):
    match = re.search(r"([\w ]*) ([A-Z]+)", source)

    if not match:
        raise NotParsableException(not_parsable_part=source)

    if len(match[2]) == 2:
        # it's an italian location
        return (match[1].strip(), 'IT')
    else:
        return (match[1].strip(), resolve_country(match[2]))


def extract_url(source) -> str:
    """
    Finds the first occurence of an URL in the string
    :param source:str
    :return:
    """
    regex = re.compile(
        r"((http|https)://)?[a-zA-Z0-9./?:@\-_=#]+\."
        r"([a-zA-Z]){2,6}([a-zA-Z0-9.&/?:@\-_=#])*"
    )
    matches = regex.search(source)
    if not matches:
        raise NotParsableException(not_parsable_part=source)
    return matches[0]


def extract_date(source: str) -> date:
    """
    Turns a italian date string into a date object
    :param source:
    :return: date
    """
    try:
        d = dateparser.parse(source).date()
        return d
    except AttributeError:
        raise NotParsableException(not_parsable_part=source)


def extract_races(source: str) -> list:
    """
    10 km / 5 km / 2 km --> [10,5,2]
    :param source:
    :return: list
    """
    matches = re.findall(r"([\d,]+) ?(k?m)(?: [/+])?", source)

    if not matches:
        raise NotParsableException(not_parsable_part=source)

    return [
        float(m[0].replace(",", ".")) / (1000 if m[1] == "m" else 1) for m in matches
    ]


def parse_line(source: str) -> dict:
    s = BeautifulSoup(source, "html.parser")
    regex = re.compile(r"– (.*?): (.*?), (.*) \((.*)\)")
    matches = regex.search(s.text)

    if not matches:
        raise NotParsableException(not_parsable_part=source)

    return {
        "date": extract_date(matches[1]),
        "event": matches[2],
        "website": extract_url(source),
        "location": resolve_location_string(matches[3]),
        "races": extract_races(matches[4]),
    }


def import_traversate() -> ImportResult:
    """
    Imports
    :return ImportResult:
    """
    r = requests.get("https://anatreselvagge.wordpress.com/2020/01/09/traversate2020/")
    soup = BeautifulSoup(r.content, "html.parser")

    eventlist = soup.select("#single > p:nth-child(3)")

    events = str(eventlist[0]).split("<br/")

    result = {"parsed_items": [], "failed_items": []}
    for event_line in events:
        try:
            result["parsed_items"].append(parse_line(event_line))
        except NotParsableException as e:
            result["failed_items"].append(
                {"source": event_line, "not_parsable_part": e.not_parsable_part}
            )

    return result
