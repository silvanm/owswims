#!/usr/bin/env python3
import subprocess
import time

# List of all 50 US states
states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New_Hampshire",
    "New_Jersey",
    "New_Mexico",
    "New_York",
    "North_Carolina",
    "North_Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode_Island",
    "South_Carolina",
    "South_Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West_Virginia",
    "Wisconsin",
    "Wyoming",
]

# Run crawl_events for each state
for state in states:
    url = f"https://raysnotebook.info/ows/schedules/{state}.html"
    command = f"python manage.py crawl_events --crawl '{url}'"

    print(f"Crawling {state}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully crawled {state}")
    except subprocess.CalledProcessError as e:
        print(f"Error crawling {state}: {e}")

    # Add a small delay between requests to avoid overloading the server
    time.sleep(1)

print("All states crawled successfully!")
