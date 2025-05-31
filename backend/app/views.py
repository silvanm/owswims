from datetime import datetime
from urllib.parse import urljoin

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django_sitemaps import Sitemap

from app import models
from owswims import settings


@xframe_options_exempt
def index(request):
    return render(request, template_name="index.html")


def sitemap(request):
    sitemap = Sitemap(
        build_absolute_uri=request.build_absolute_uri,
    )

    # needs to correspond to the frontend
    other_languages = ["de", "fr", "it", "es", "ru", "ja"]

    # Homepage
    sitemap.add(
        "/en/",
        changefreq="monthly",
        priority=1,
        alternates={code: urljoin("/", code) for code in other_languages},
    )

    # Eventpages
    events = models.Event.objects.filter(date_start__gte=datetime.now())
    for event in events:
        url = f"/event/{event.slug}"
        sitemap.add(
            url,
            changefreq="monthly",
            priority=0.5,
            alternates={code: f"/{code}{url}" for code in other_languages},
            lastmod=event.edited_at,
        )

    # Organizer pages
    organizers = models.Organizer.objects.filter(
        events__date_start__gte=datetime.now()
    ).distinct()
    for organizer in organizers:
        if organizer.slug:  # Only add if organizer has a slug
            url = f"/organizer/{organizer.slug}"
            sitemap.add(
                url,
                changefreq="monthly",
                priority=0.7,
                alternates={code: f"/{code}{url}" for code in other_languages},
            )

    return sitemap.response(
        # pretty_print is False by default
        pretty_print=settings.DEBUG,
    )
