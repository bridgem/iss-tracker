# Get TLE (Two Line Entry) for astronomical objects
# URL returns all known satellites three lines at a time (name + 2 data lines)
# Example for the ISS:
# ISS (ZARYA)
# 1 25544U 98067A   20335.58619075  .00005341  00000-0  10461-3 0  9992
# 2 25544  51.6473 245.1182 0001968  95.8013 325.6569 15.49119345257812
#

import requests
STATIONS_URL = 'https://celestrak.com/NORAD/elements/stations.txt'


def get_tle(station_name):
	resp = requests.get(STATIONS_URL)
	tle_data = resp.text.splitlines()

	found = False
	tle_line1 = ""
	tle_line2 = ""
	# Each entry is 3 lines (includes name on it's own line), so go through the list 3 lines at a time
	for i in range(0, len(tle_data)-2, 3):
		name = tle_data[i].rstrip()

		if name == station_name:
			found = True
			# Found the required station name, so read the TLE from the next 2 lines
			tle_line1 = tle_data[i+1]
			tle_line2 = tle_data[i+2]
			break

	return found, tle_line1, tle_line2
