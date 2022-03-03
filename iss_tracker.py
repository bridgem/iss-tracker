# iss_tracker.py
# Show ISS position data and nearest place from a list of places
# Single line text output, or curses character based screen (-c switch)
#
# Martin Bridge, Jun 2021

# Credits:
# https://celestrak.com/NORAD/elements/stations.txt
# http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html

import argparse
import math
import time
from datetime import datetime, timedelta
import curses
import os
from pyfiglet import Figlet
import sys
from skyfield.api import Topos, load, EarthSatellite
from get_tle import get_tle
from places import closest_place_to, latlong, place

DEG_PER_RAD = 180.0 / math.pi
OBSERVER_HOME = 'London'
OBSERVER_LAT = 51.4771556
OBSERVER_LON = 0.0
OBSERVER_ELEV = 10
SAT_NAME = 'ISS (ZARYA)'


CURSES = False
FIRST_DATA_LINE = 9    # First line on screen for data output
# figlet fonts: chunky doom graffiti speed big slant crawford roman  stop univers
figfont = Figlet(font='slant', width=200)

alt_sym = "Alt:"
az_sym = "Az:"


def get_obs_date():
	# Return date for observation
	# Useful for debug
	# TODO: Could specify as a commmand line parameter for a fixed time
	# return ts.utc(2020, 12, 14, 23, 37, 25.511375)
	return ts.now()


def init_screen():
	if CURSES:
		scr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		scr.nodelay(True)
		scr.keypad(1)
		scr.clear()
		scr.addstr(1, 1, figfont.renderText('Satellite Tracker'))
		return scr
	else:
		return None


def display_headers(screen, sat_name, tle_line1, tle_line2):
	year = 2000 + int(tle_line1[18:20])
	decimal_days = float(tle_line1[20:32])
	epoch = datetime(year, 1, 1) + timedelta(decimal_days - 1)
	d = epoch.strftime("%a %d %b %Y %H:%M:%S")

	if CURSES:
		screen.addstr(FIRST_DATA_LINE - 2,  1, ''.ljust(82,'_'))
		screen.addstr(FIRST_DATA_LINE,  1, f'Object:      {sat_name}')
		screen.addstr(FIRST_DATA_LINE + 1, 1, f'TLE1:        {tle_line1}')
		screen.addstr(FIRST_DATA_LINE + 2, 1, f'TLE2:        {tle_line2}')
		screen.addstr(FIRST_DATA_LINE + 4, 1, f'TLE Epoc     {d}')

		# Data Labels
		screen.addstr(FIRST_DATA_LINE + 5, 1, 'Time Now')

		screen.addstr(FIRST_DATA_LINE + 7, 1, 'Observer', curses.A_BOLD)
		screen.addstr(FIRST_DATA_LINE + 8, 1, 'Lat')
		screen.addstr(FIRST_DATA_LINE + 9, 1, 'Lon')

		screen.addstr(FIRST_DATA_LINE + 7, 28, 'Sat', curses.A_BOLD)
		screen.addstr(FIRST_DATA_LINE + 8, 28, 'Lat')
		screen.addstr(FIRST_DATA_LINE + 9, 28, 'Lon')
		screen.addstr(FIRST_DATA_LINE + 10, 28, 'Altitude')

		screen.addstr(FIRST_DATA_LINE + 8, 54, 'Elevation')
		screen.addstr(FIRST_DATA_LINE + 9, 54, 'Azimuth')
		screen.addstr(FIRST_DATA_LINE + 10, 54, 'Range')

		screen.addstr(FIRST_DATA_LINE + 12, 1, f'{"Nearest OCI Region:"}')
	else:
		print(sat_name)
		print(tle_line1)
		print(tle_line2)
		print(f'TLE Epoch: {d}')
		print()


def update_screen(screen, observer_name, observer: Topos, sat: EarthSatellite):
	t = get_obs_date()

	geocentric = sat.at(t)
	subpoint = geocentric.subpoint()

	dlat = subpoint.latitude.degrees
	dlon = subpoint.longitude.degrees
	delev = int(subpoint.elevation.km)

	# Display value units, degrees & km
	difference = sat - observer
	topocentric = difference.at(t)
	alt, az, distance = topocentric.altaz()

	# Find closest place/city from list
	nearest_city, dist = closest_place_to(latlong(dlat, dlon))

	nearest_loc = nearest_city.id

	if CURSES:
		n = datetime.utcnow()
		nowstr = n.strftime('%a %d %b %Y %H:%M:%S.%f %Z')
		screen.addstr(FIRST_DATA_LINE + 5, 14, nowstr)

		screen.addstr(FIRST_DATA_LINE + 7, 10, f'{observer_name:>12s}', curses.A_BOLD)
		screen.addstr(FIRST_DATA_LINE + 8, 10, f'{observer.latitude.degrees:>12.4f}')
		screen.addstr(FIRST_DATA_LINE + 9, 10, f'{observer.longitude.degrees:>12.4f}')

		screen.addstr(FIRST_DATA_LINE + 7, 36, f'{sat.name:>12s}', curses.A_BOLD)
		screen.addstr(FIRST_DATA_LINE + 8, 36, f'{dlat:>12.4f}')
		screen.addstr(FIRST_DATA_LINE + 9, 36, f'{dlon:>12.4f}')
		screen.addstr(FIRST_DATA_LINE + 10, 37, f'{delev:>6.0f} km')

		screen.addstr(FIRST_DATA_LINE + 8, 64, f'{alt.degrees:>10.4f} deg')
		screen.addstr(FIRST_DATA_LINE + 9, 64, f'{az.degrees:>10.4f} deg')
		screen.addstr(FIRST_DATA_LINE + 10, 63, f'{distance.km:>6.0f} km')

		screen.addstr(FIRST_DATA_LINE + 14,  1, f'{nearest_loc:17s} {int(dist):5d} km', curses.A_BOLD)
		screen.addstr(FIRST_DATA_LINE + 17, 1, '')
		screen.refresh()

	else:
		# print(f'{t.utc_strftime("%Y-%m-%d %H:%M:%S.%f")} Obs: {observer_name:12s} {observer.latitude.degrees:8.4f} ,{observer.longitude.degrees:9.4f}')
		print(f'{t.utc_strftime("%Y-%m-%d %H:%M:%S.%f")} Pos: {sat.name:12s} {dlat:8.4f} ,{dlon:9.4f}   '
		      f'{alt_sym} {alt.degrees:>5.1f}  {az_sym} {az.degrees:>5.1f}  '
		      f'Ht: {delev:3.0f} km  Range: {distance.km:5.0f} km  '
		      f' Nearest: {nearest_loc:12s} {int(dist):4d} km')


def reset_terminal(screen):
	if CURSES:
		screen.keypad(0)
		curses.echo()
		curses.nocbreak()
		curses.endwin()


def get_input(screen):
	if CURSES:
		# stay in this loop till the user presses 'q'
		ch = screen.getch()
		if ch == ord('q'):
			reset_terminal(screen)
			sys.exit()
		elif ch == ord('r'):
			# Restart
			os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":

	try:
		CURSES = False
		parser = argparse.ArgumentParser(description='Satellite Tracker')
		parser.add_argument('-c', '--curses', help='Use curses output', action='store_true')
		args = parser.parse_args()
		CURSES = args.curses

		screen = init_screen()

		found, tle_line1, tle_line2 = get_tle(SAT_NAME)

		if not found:
			print(f"Error: Satellite '{SAT_NAME}' not found")
		else:
			ts = load.timescale()
			sat = EarthSatellite(tle_line1, tle_line2, SAT_NAME, ts)
			observer = Topos(OBSERVER_LAT, OBSERVER_LON, elevation_m=OBSERVER_ELEV)

			display_headers(screen, SAT_NAME, tle_line1, tle_line2)

			while True:
				update_screen(screen, OBSERVER_HOME, observer, sat)
				time.sleep(1.0)

				get_input(screen)

	finally:
		reset_terminal(screen)