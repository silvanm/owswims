from datetime import date

import pytest
from django_countries import countries

import app.importer.traversate as traversate

raw_events = [
    '– <span style="color:#008000;">Sabato 11 dicembre</span>: '
    '<a href="http://oceanman-openwater.com/2020-races/oceanman-bali-2020/" '
    'rel="noopener noreferrer" target="_blank"><span style="color:#333399;">'
    "OceanMan Bali</span>"
    "</a>, <em>Bali INDONESIA</em> (10 km / 5 km / 1,5 km)</p>",
    '– Domenica 8 novembre: <a href="http://oceanman-openwater.com/2020-races/"'
    ' rel="noopener noreferrer" target="_blank"><span style="color:#333399;">OceanMan '
    "Cyprus</span></a>, <em>Larnaca CIPRO</em> (10 km / 6 km / 2 km)",
    '– <del datetime="2020-08-03T00:13:43+00:00">Domenica 8 novembre: '
    '<a href="http://oceanman-openwater.com/2020-races/oceanman-alanya-2020/"'
    ' rel="noopener noreferrer" target="_blank"><span style="color:#333399;">'
    "OceanMan Alanya</span></a>, <em>Alanya TURCHIA</em> (10 km / 5 km / 2 km)</del>",
    '– <span style="color:#008000;">Venerdì 30 – Sabato 31 ottobre</span>:'
    ' <a href="http://oceanman-openwater.com/2020-races/oceanman-sahl-2020/"'
    ' rel="noopener noreferrer" target="_blank"><span style="color:#333399;">'
    "OceanMan Sahl Hasheesh</span></a>, <em>Hurghada EGITTO</em> (10 km / 5 km / 1,5 km)",
]


testdata_urls = [
    (
        raw_events[0],
        "http://oceanman-openwater.com/2020-races/oceanman-bali-2020/",
    ),
    (
        raw_events[1],
        "http://oceanman-openwater.com/2020-races/",
    ),
]


@pytest.mark.parametrize("a,expected", testdata_urls)
def test_extract_url(a, expected):
    url = traversate.extract_url(a)
    assert url == expected


testdata_date = [
    (
        "Sabato 11 dicembre",
        date(year=2020, month=12, day=11),
    ),
    (
        "Domenica 8 novembre",
        date(year=2020, month=11, day=8),
    ),
]


@pytest.mark.parametrize("a,expected", testdata_date)
def test_extract_date(a, expected):
    dt = traversate.extract_date(a)
    assert dt == expected


testdata_line = [
    (
        raw_events[0],
        {
            "date": date(2020, 12, 11),
            "event": "OceanMan Bali",
            "location": ("Bali", "ID"),
            "races": [10.0, 5.0, 1.5],
            "website": "http://oceanman-openwater.com/2020-races/oceanman-bali-2020/",
        },
    ),
    (
        '– Domenica 8 novembre: <a href="http://oceanman-openwater.com/2020-races/" '
        'rel="noopener noreferrer" '
        'target="_blank"><span style="color:#333399;">OceanMan Cyprus</span></a>, '
        "<em>Larnaca CIPRO</em> "
        "(10 km / 6 km / 2 km)",
        {
            "date": date(2020, 11, 8),
            "event": "OceanMan Cyprus",
            "location": ("Larnaca", "CY"),
            "races": [10.0, 6.0, 2.0],
            "website": "http://oceanman-openwater.com/2020-races/",
        },
    ),
    (
        '– <del datetime="2020-08-03T00:13:43+00:00">Domenica 8 novembre: '
        '<a href="http://oceanman-openwater.com/2020-races/oceanman-alanya-2020/" '
        'rel="noopener noreferrer" '
        'target="_blank"><span style="color:#333399;">OceanMan Alanya</span></a>, '
        "<em>Alanya TURCHIA</em> "
        "(10 km / 5 km / 2 km)</del>→ annullato",
        {
            "date": date(2020, 11, 8),
            "event": "OceanMan Alanya",
            "location": ("Alanya", "TR"),
            "races": [10.0, 5.0, 2.0],
            "website": "http://oceanman-openwater.com/2020-races/oceanman-alanya-2020/",
        },
    ),
]


@pytest.mark.parametrize("a,expected", testdata_line)
def test_parse_line(a, expected):
    struct = traversate.parse_line(a)
    assert struct == expected


def test_country_it_to_country_obj():
    assert traversate.resolve_country("CIPRO") == "CY"


def test_country_it_to_country_obj_invalid_country():
    with pytest.raises(traversate.NotParsableException):
        traversate.resolve_country("foo")


testdata_location = [
    ("Alanya TURCHIA", ("Alanya", "TR")),
    ("Omegna VB", ("Omegna", "IT")),
]


@pytest.mark.parametrize("a,expected", testdata_location)
def test_resolve_location_string(a, expected):
    assert traversate.resolve_location_string(a) == expected


testdata_races = [("15 km", [15.0]), ("500 m", [0.5]), ("500 m / 15 km", [0.5, 15.0])]


@pytest.mark.parametrize("a,expected", testdata_races)
def test_extract_races(a, expected):
    assert traversate.extract_races(a) == expected


def test_import_traversate():
    # result = import_traversate()
    # print(result)
    assert True
