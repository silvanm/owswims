from django.core.management.base import BaseCommand
from app.crawl_profiles.profiles import get_available_profiles, get_profile


class Command(BaseCommand):
    help = "List available crawl profiles"

    def handle(self, *args, **options):
        profiles = get_available_profiles()

        if not profiles:
            self.stdout.write(self.style.WARNING("No crawl profiles found"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(profiles)} crawl profiles:"))

        for profile_id in profiles:
            profile = get_profile(profile_id)
            name = profile.get("name", profile_id) if profile else profile_id
            start_url = (
                profile.get("start_url", "No start URL")
                if profile
                else "Invalid profile"
            )
            description = profile.get("description", "") if profile else ""

            self.stdout.write(f"- {profile_id}: {name}")
            self.stdout.write(f"  URL: {start_url}")

            if description:
                self.stdout.write(f"  Description: {description}")

            # Show actions count if available
            if profile and "actions" in profile:
                action_count = len(profile["actions"])
                self.stdout.write(f"  Actions: {action_count}")

            self.stdout.write("")  # Empty line between profiles
