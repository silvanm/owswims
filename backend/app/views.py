from datetime import datetime
from urllib.parse import urljoin

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django_sitemaps import Sitemap

from app import models
from app.models import ClaimToken
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

    # Info pages
    info_tabs = ["help", "organizers", "contributors", "imprint"]
    for tab in info_tabs:
        url = f"/en/info/{tab}"
        sitemap.add(
            url,
            changefreq="yearly",
            priority=0.3,
            alternates={
                code: f"/{code}/info/{tab}" for code in other_languages
            },
        )

    # Eventpages
    events = models.Event.objects.filter(date_start__gte=datetime.now())
    for event in events:
        url = f"/en/event/{event.slug}"
        sitemap.add(
            url,
            changefreq="monthly",
            priority=0.5,
            alternates={
                code: f"/{code}/event/{event.slug}" for code in other_languages
            },
            lastmod=event.edited_at,
        )

    # Organizer pages
    organizers = models.Organizer.objects.filter(
        events__date_start__gte=datetime.now()
    ).distinct()
    for organizer in organizers:
        if organizer.slug:  # Only add if organizer has a slug
            url = f"/en/organizer/{organizer.slug}"
            sitemap.add(
                url,
                changefreq="monthly",
                priority=0.7,
                alternates={
                    code: f"/{code}/organizer/{organizer.slug}"
                    for code in other_languages
                },
            )

    return sitemap.response(
        # pretty_print is False by default
        pretty_print=settings.DEBUG,
    )


def organizer_stats(request):
    """Return organizer statistics, optionally filtered by country."""
    country = request.GET.get('country', '')

    if country:
        # Filter organizers by country through their events' locations
        organizers = models.Organizer.objects.raw(
            "SELECT * FROM app_organizer WHERE id IN "
            "(SELECT DISTINCT organizer_id FROM app_event "
            "WHERE location_id IN (SELECT id FROM app_location WHERE country = '%s'))" % country
        )
    else:
        organizers = models.Organizer.objects.all()

    results = []
    for org in organizers:
        event_count = org.event_set.count()
        results.append({
            'name': org.name,
            'email': org.contact_email,
            'website': org.website,
            'event_count': event_count,
        })

    return JsonResponse({'organizers': results})


def claim_organizer(request, token):
    """
    View for organizers to claim their profile by setting a password.

    GET: Show password set form
    POST: Create user, link to organizer, log in, redirect to organizer admin
    """
    claim_token = get_object_or_404(ClaimToken, token=token)

    # Check if token is valid
    if not claim_token.is_valid():
        return render(
            request,
            "claim/invalid_token.html",
            {"reason": "used" if claim_token.used_at else "expired"},
        )

    organizer = claim_token.organizer

    # Check if organizer already has a user linked
    if organizer.user:
        return render(
            request,
            "claim/already_claimed.html",
            {"organizer": organizer},
        )

    if request.method == "POST":
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        errors = []

        # Validate passwords
        if not password:
            errors.append(_("Password is required."))
        elif len(password) < 8:
            errors.append(_("Password must be at least 8 characters."))
        elif password != password_confirm:
            errors.append(_("Passwords do not match."))

        if errors:
            return render(
                request,
                "claim/set_password.html",
                {"organizer": organizer, "errors": errors},
            )

        # Create user with organizer's email
        email = organizer.contact_email
        if not email:
            errors.append(_("Organizer does not have a contact email set. Please contact support."))
            return render(
                request,
                "claim/set_password.html",
                {"organizer": organizer, "errors": errors},
            )
        username = email  # Use email as username

        # Check if user with this email already exists
        if User.objects.filter(username=username).exists():
            # Link existing user to organizer
            user = User.objects.get(username=username)
            # Ensure existing user has staff access for organizer portal
            if not user.is_staff:
                user.is_staff = True
                user.save()
        else:
            # Create new user with staff access for organizer portal
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.is_staff = True
            user.save()

        # Link user to organizer
        organizer.user = user
        organizer.save()

        # Mark token as used
        claim_token.used_at = timezone.now()
        claim_token.save()

        # Log user in (specify backend since multiple auth backends are configured)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        # Redirect to organizer admin
        return redirect("organizer_admin:index")

    return render(
        request,
        "claim/set_password.html",
        {"organizer": organizer},
    )
