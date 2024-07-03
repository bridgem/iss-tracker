# Get TLE (Two Line Entry) for astronomical objects
# URL returns all known satellites three lines at a time (name + 2 data lines)
# Example for the ISS:
# ISS (ZARYA)
# 1 25544U 98067A   20335.58619075  .00005341  00000-0  10461-3 0  9992
# 2 25544  51.6473 245.1182 0001968  95.8013 325.6569 15.49119345257812
#
# 13-jan-2023   Cache the stations file to avoid excessive requests to this rate limited service

import os
import requests
import time
from datetime import datetime, timedelta
from itertools import islice
from dataclasses import dataclass, field

STATIONS_URL = 'https://celestrak.com/NORAD/elements/stations.txt'
LOCAL_FILE = 'stations.txt'

@dataclass
class TLE:
	sat_name: str
	line1: str = field(init=False)
	line2: str = field(init=False)
	epoch: str = field(init=False)
	found: bool = False

	def __post_init__(self):
		# self.found, self.line1, self.line2 = self.get_tle()
		self.get_tle()
		if self.found:
			year = 2000 + int(self.line1[18:20])
			decimal_days = float(self.line1[20:32])
			epoch = datetime(year, 1, 1) + timedelta(decimal_days - 1)
			self.epoch = epoch.strftime("%a %d %b %Y %H:%M:%S")

	def is_valid(self):
		return self.found

	def get_tle(self):
		station_name = self.sat_name

		maximum_age = 86400  # 1 day in seconds

		# Check for cached copy of stations file, which must me
		# 1. present
		# 2. newer than maximum_age
		# 3. non-zero length
		fetch_required = False
		if not os.path.exists(LOCAL_FILE):
			fetch_required = True
		else:
			file_stat = os.stat(LOCAL_FILE)
			modified_time = file_stat.st_mtime
			file_size = file_stat.st_size
			now = time.time()
			if (now - modified_time) > maximum_age or file_size == 0:
				fetch_required = True

		if fetch_required:
			resp = requests.get(STATIONS_URL)

			# Save to local file
			with open(LOCAL_FILE, "wb") as f:
				f.write(resp.content)

		self.found = False

		with open(LOCAL_FILE, 'r') as infile:
			while not self.found:
				# Each entry is 3 lines (includes name on its own line), so go through the list 3 lines at a time
				tle_data = list(islice(infile, 3))
				name = tle_data[0].rstrip()

				if name == station_name:
					self.found = True
					# Found the required station name, so read the TLE from the next 2 lines
					self.line1 = tle_data[1].strip()
					self.line2 = tle_data[2].strip()
					break
				if not tle_data:
					break

		# return found, tle_line1, tle_line2
		return
