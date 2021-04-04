from __future__ import print_function

import json
import os.path
import re

import dateparser
from django.core.management import BaseCommand
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1WbhyilJWO6I9JVfPSIkGo2KqpdqnCsuN75nh56q0U-8'
SAMPLE_RANGE_NAME = 'A2:E73'

CONVERSION_FACTOR = {
    'м': 0.001,
    'км': 1,
    'миля': 1.609
}


class Command(BaseCommand):

    def handle(self, *args, **options):
        creds = service_account.Credentials.from_service_account_file(
            '/Users/silvan.muehlemann/PycharmProjects/owswims/backend/owswims-cc29cfd6d273.json', scopes=SCOPES,
        )
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        out = []

        for in_row in values:
            print(in_row)
            out_row = {}
            out_row['name'] = in_row[1]
            out_row['location'] = in_row[2]

            # convert 4-5.09.2021 to a different start/enddate
            m = re.match(r'(\d+)(?:-(\d+))?\.(.*?)$', in_row[0])
            out_row['date_start'] = dateparser.parse(f"{m.group(1)}.{m.group(3)}").strftime(
                '%Y-%m-%d')
            if m.group(2):
                out_row['date_end'] = dateparser.parse(f"{m.group(2)}.{m.group(3)}").strftime(
                    '%Y-%m-%d')
            else:
                out_row['date_end'] = out_row['date_start']

            matches = re.findall(r'([\d.]+?) ?(м|км|миля)', in_row[3])

            out_row['races'] = [float(v[0]) * CONVERSION_FACTOR[v[1]] for v in matches]

            out_row['website'] = in_row[4]
            if len(out_row['races']) > 0:
                out.append(out_row)
        self.stdout.write(json.dumps(out, indent=True))
