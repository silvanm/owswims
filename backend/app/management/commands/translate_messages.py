"""
Management command to translate Django .po files using OpenAI LLM.

Usage:
    python manage.py translate_messages              # Translate all languages
    python manage.py translate_messages --lang de   # Translate specific language
    python manage.py translate_messages --dry-run   # Preview without saving
"""

import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from openai import OpenAI


# Language names for context in prompts
LANGUAGE_NAMES = {
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "es": "Spanish",
    "ru": "Russian",
    "ja": "Japanese",
}


class Command(BaseCommand):
    help = "Translate Django .po files using OpenAI LLM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            type=str,
            help="Specific language code to translate (e.g., de, fr). If not provided, translates all.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview translations without saving to files.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-translate even if translation already exists.",
        )

    def handle(self, *args, **options):
        lang = options.get("lang")
        dry_run = options.get("dry_run")
        force = options.get("force")

        # Initialize OpenAI client
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            self.stderr.write(self.style.ERROR("OPENAI_API_KEY not configured"))
            return

        client = OpenAI(api_key=api_key)

        # Determine which languages to process
        if lang:
            if lang not in LANGUAGE_NAMES:
                self.stderr.write(
                    self.style.ERROR(f"Unknown language: {lang}. Available: {list(LANGUAGE_NAMES.keys())}")
                )
                return
            languages = [lang]
        else:
            languages = list(LANGUAGE_NAMES.keys())

        locale_path = settings.LOCALE_PATHS[0] if settings.LOCALE_PATHS else Path(settings.BASE_DIR) / "locale"

        for lang_code in languages:
            po_file = locale_path / lang_code / "LC_MESSAGES" / "django.po"

            if not po_file.exists():
                self.stderr.write(self.style.WARNING(f"No .po file found for {lang_code}: {po_file}"))
                continue

            self.stdout.write(f"\nProcessing {LANGUAGE_NAMES[lang_code]} ({lang_code})...")
            self._translate_po_file(client, po_file, lang_code, dry_run, force)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("\nDone! Run 'python manage.py compilemessages' to compile translations.")
            )

    def _translate_po_file(self, client, po_file: Path, lang_code: str, dry_run: bool, force: bool):
        """Parse and translate a .po file."""
        content = po_file.read_text(encoding="utf-8")

        # Parse entries from .po file
        entries = self._parse_po_entries(content)

        # Filter entries that need translation
        to_translate = []
        for entry in entries:
            if not entry["msgid"]:  # Skip empty msgids (header)
                continue
            if entry["msgstr"] and not force:  # Skip already translated unless --force
                continue
            to_translate.append(entry)

        if not to_translate:
            self.stdout.write(f"  No new strings to translate for {lang_code}")
            return

        self.stdout.write(f"  Translating {len(to_translate)} strings...")

        # Batch translate for efficiency
        translations = self._batch_translate(client, to_translate, lang_code)

        if dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN] Would translate:"))
            for entry, translation in zip(to_translate, translations):
                self.stdout.write(f"    EN: {entry['msgid'][:60]}...")
                self.stdout.write(f"    {lang_code.upper()}: {translation[:60]}...")
            return

        # Update entries with translations
        for entry, translation in zip(to_translate, translations):
            entry["msgstr"] = translation

        # Write updated content back to file
        updated_content = self._rebuild_po_content(content, entries)
        po_file.write_text(updated_content, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"  Updated {po_file}"))

    def _parse_po_entries(self, content: str) -> list:
        """Parse .po file content into structured entries."""
        entries = []
        current_entry = {"msgid": "", "msgstr": "", "comments": [], "flags": []}

        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Comments
            if line.startswith("#"):
                if line.startswith("#,"):
                    current_entry["flags"].append(line)
                else:
                    current_entry["comments"].append(line)
                i += 1
                continue

            # msgid (can be multiline)
            if line.startswith("msgid "):
                msgid_parts = [self._extract_string(line[6:])]
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    msgid_parts.append(self._extract_string(lines[i]))
                    i += 1
                current_entry["msgid"] = "".join(msgid_parts)
                continue

            # msgstr (can be multiline)
            if line.startswith("msgstr "):
                msgstr_parts = [self._extract_string(line[7:])]
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    msgstr_parts.append(self._extract_string(lines[i]))
                    i += 1
                current_entry["msgstr"] = "".join(msgstr_parts)

                # Entry complete, save and reset
                entries.append(current_entry)
                current_entry = {"msgid": "", "msgstr": "", "comments": [], "flags": []}
                continue

            i += 1

        return entries

    def _extract_string(self, s: str) -> str:
        """Extract string from .po quoted format."""
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        # Unescape common escapes
        s = s.replace('\\"', '"').replace("\\n", "\n")
        return s

    def _batch_translate(self, client, entries: list, lang_code: str) -> list:
        """Translate multiple entries in a single API call for efficiency."""
        language_name = LANGUAGE_NAMES[lang_code]

        # Prepare the prompt
        source_strings = [entry["msgid"] for entry in entries]
        numbered_strings = "\n".join([f"{i+1}. {s}" for i, s in enumerate(source_strings)])

        prompt = f"""Translate the following English strings to {language_name} for a swimming event management website.

Context: These are UI strings for an admin portal where swimming event organizers manage their events.
Keep translations concise and professional. Preserve any special characters, placeholders like %(name)s or {{0}}, and formatting.

English strings to translate (numbered):
{numbered_strings}

Respond with ONLY the translations, numbered to match the input. No explanations or extra text.
Format: One translation per line, starting with the number and a period."""

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator specializing in {language_name} translations for web applications. Translate accurately while maintaining natural {language_name} phrasing.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
            )

            # Parse response
            response_text = response.choices[0].message.content.strip()
            translations = self._parse_numbered_response(response_text, len(entries))

            return translations

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Translation API error: {e}"))
            return [""] * len(entries)

    def _parse_numbered_response(self, response: str, expected_count: int) -> list:
        """Parse numbered response from LLM."""
        translations = []
        lines = response.strip().split("\n")

        for line in lines:
            # Match patterns like "1. translation" or "1) translation"
            match = re.match(r"^\d+[\.\)]\s*(.+)$", line.strip())
            if match:
                translations.append(match.group(1).strip())

        # Pad with empty strings if we didn't get enough translations
        while len(translations) < expected_count:
            translations.append("")

        return translations[:expected_count]

    def _rebuild_po_content(self, original_content: str, entries: list) -> str:
        """Rebuild .po file content with updated translations."""
        # Build a lookup dict for translations
        translations = {e["msgid"]: e["msgstr"] for e in entries if e["msgid"]}

        lines = original_content.split("\n")
        result = []
        i = 0
        current_msgid = None

        while i < len(lines):
            line = lines[i]

            # Track current msgid
            if line.startswith("msgid "):
                msgid_parts = [self._extract_string(line[6:])]
                result.append(line)
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    msgid_parts.append(self._extract_string(lines[i]))
                    result.append(lines[i])
                    i += 1
                current_msgid = "".join(msgid_parts)
                continue

            # Update msgstr with translation
            if line.startswith("msgstr "):
                if current_msgid and current_msgid in translations and translations[current_msgid]:
                    # Escape the translation for .po format
                    escaped = translations[current_msgid].replace('"', '\\"').replace("\n", "\\n")
                    result.append(f'msgstr "{escaped}"')
                    # Skip any continuation lines
                    i += 1
                    while i < len(lines) and lines[i].startswith('"'):
                        i += 1
                    continue
                else:
                    result.append(line)
                    i += 1
                    continue

            result.append(line)
            i += 1

        return "\n".join(result)
