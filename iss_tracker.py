#!python
# iss_tracker.py
# Show ISS position data and nearest place from a list of places
# Single line text output, or curses character based screen (-c switch)
#
# Martin Bridge, Jun 2021
# 27-jul-2024	Use python rich instead of curses

# Credits:
# https://celestrak.com/NORAD/elements/stations.txt
# http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html

import argparse
import math
import time
from datetime import datetime, timedelta
from pyfiglet import Figlet
from dataclasses import dataclass

# Astro calculations
from skyfield.api import Topos, load, EarthSatellite

# Rich text
from rich.align import Align
from rich.style import Style
from rich.columns import Columns
from rich.console import Group
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

# Local
from get_tle import TLE
from places import closest_place_to, latlong

DEG_PER_RAD = 180.0 / math.pi
OBSERVER_TITLE = 'London'
OBSERVER_LAT = 51.4779139
OBSERVER_LON = -0.0040497
OBSERVER_ELEV = 10
SAT_NAME = 'ISS (ZARYA)'
# figlet fonts: chunky doom graffiti speed big slant crawford roman  stop univers
FIGFONTNAME = "slant"

ALT_SYM = "Alt:"
AZ_SYM = "Az:"


@dataclass
class Tracker:
	# def __init__(self, output_type, tle: TLE, observer: Topos, sat: EarthSatellite):
	output_type: str
	observer_name: str
	tle: TLE
	observer: Topos
	sat: EarthSatellite

	def __post_init__(self):
		# Define rich layout
		if output_type == "rich":
			self.layout = Layout(name="screen")
			self.layout.split_column(
				Layout(name="header", size=6),
				Layout(name="upper", size=8),
				Layout(name="lower"),   # size=8),
				Layout(name="footer", size=3),
			)
			self.layout["lower"].split_row(
				Layout(name="left", size=34),
				Layout(name="right")
			)

	def __update_sat(self):
		self.t = ts.now()
		geocentric = sat.at(self.t)
		subpoint = geocentric.subpoint()

		self.sat_lat = subpoint.latitude.degrees
		self.sat_lon = subpoint.longitude.degrees
		self.sat_elev = subpoint.elevation.km

		# Display value units, degrees & km
		difference = sat - observer
		topocentric = difference.at(self.t)
		self.obs_sat_alt, self.obs_sat_az, self.obs_sat_distance = topocentric.altaz()

		# Find the closest place/city from list
		self.sat_nearest_city, self.sat_city_dist = closest_place_to(latlong(self.sat_lat, self.sat_lon))
		nearest_loc = f"{self.sat_nearest_city.id}, {self.sat_nearest_city.name}"
		self.nearest_with_dist = f"{nearest_loc} ({int(self.sat_city_dist)} km)"

		# Calculate speed from velocity vector
		v = geocentric.velocity.km_per_s
		self.vkms = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
		self.vkmh = self.vkms * 3600
		self.vmph = self.vkmh * 0.621371

	# def update_screen(self, observer_name, observer: Topos, tle: TLE, sat: EarthSatellite):
	def update_screen(self):
		# Update satellite position
		self.__update_sat()

		# Output the data
		# Screen header title
		figfont = Figlet(font=FIGFONTNAME, width=200)
		ascii_art = figfont.renderText('Satellite Tracker').rstrip()

		if self.output_type == "list":
			print(f'{self.t.utc_strftime("%Y-%m-%d %H:%M:%S")} Pos: {self.sat_lat:8.4f}, {self.sat_lon:9.4f}   '
				  f'{ALT_SYM} {self.obs_sat_alt.degrees:>5.1f}  {AZ_SYM} {self.obs_sat_az.degrees:>5.1f}  '
				  f'Ht: {self.sat_elev:3.0f} km  Range: {self.obs_sat_distance.km:5.0f} km  '
				  f' Nearest: {self.nearest_with_dist}')

		elif self.output_type == "rich":
			author = "by Martin Bridge"
			heading_group = Group(
				Align(Text(ascii_art.rstrip(), style="bold"), align="center"),
				Align(Text(author, Style(dim=True, italic=True, color="#aaaaaa")), align="right"),
			)

			# Define the TLE details as a Table
			object_table = Table(show_header=False, show_lines=False, show_edge=False, show_footer=False)
			object_table.add_row("Object:", sat.name)
			object_table.add_row("TLE1:", tle.line1)
			object_table.add_row("TLE2:", tle.line2)
			object_table.add_row("TLE Epoch:", tle.epoch)

			n = datetime.utcnow()
			nowstr = n.strftime('%a %d %b %Y %H:%M:%S.%f %Z')
			object_table.add_row("", "")
			object_table.add_row("Time Now: ", nowstr)

			# Define the observation details as a Table
			obs_table = Table(show_header=False, show_lines=False, show_edge=True, show_footer=False, header_style="bold magenta")
			obs_table.add_column(f"Observer: {self.observer_name}")
			obs_table.add_row("Latitude", f"{observer.latitude.degrees:10.4f}")
			obs_table.add_row("Longitude", f"{observer.longitude.degrees:10.4f}")
			obs_table.add_row("Range", f"{self.obs_sat_distance.km:5.0f} km")

			sat_table = Table(show_header=False, show_lines=False, show_edge=True, show_footer=False, header_style="bold magenta")
			sat_table.add_column("Satellite")
			sat_table.add_row("Latitude", f"{self.sat_lat:10.4f}")
			sat_table.add_row("Longitude", f"{self.sat_lon:10.4f}")
			sat_table.add_row("Altitude", f"{self.sat_elev:5.0f} km")
			sat_table.add_row("Speed", f"{self.vkmh:5.0f} km/h")
			sat_table.add_row("", f"{self.vmph:5.0f} mph")

			sat_table2 = Table(show_header=False, show_lines=False, show_edge=True, show_footer=False, header_style="bold magenta")
			sat_table2.add_row("Elevation", f"{self.obs_sat_alt.degrees:10.4f} deg")
			sat_table2.add_row("Azimuth", f"{self.obs_sat_az.degrees:10.4f} deg")

			# Panels
			tle_panel = Panel(object_table, title="Satellite Information", title_align="left", border_style="green")
			obs_panel = Panel(obs_table, title="Observer: London", title_align="left", border_style="cyan")
			sat_panel = Panel(Columns([sat_table, sat_table2]), title=f"Satellite: {sat.name}", title_align="left", border_style="cyan")
			status_panel = Panel(Text(self.nearest_with_dist), title="Nearest Place", title_align="left", border_style="cyan")

			self.layout["header"].update(heading_group)
			self.layout["upper"].update(tle_panel)
			self.layout["left"].update(obs_panel)
			self.layout["right"].update(sat_panel)
			self.layout["footer"].update(status_panel)


def print_tle(tle):
	print(tle.sat_name)
	print(tle.line1)
	print(tle.line2)
	print(f'TLE Epoch: {tle.epoch}')
	print()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Satellite Tracker')
	parser.add_argument('-r', '--rich', help='Use rich output on live screen', action='store_true')
	args = parser.parse_args()
	output_type = "rich" if args.rich else "list"

	try:
		tle = TLE(SAT_NAME)

		if not tle.is_valid():
			print(f"Error: Satellite '{SAT_NAME}' not found")
		else:
			ts = load.timescale()
			sat = EarthSatellite(tle.line1, tle.line2, SAT_NAME, ts)
			observer = Topos(OBSERVER_LAT, OBSERVER_LON, elevation_m=OBSERVER_ELEV)

			screen = Tracker(output_type, OBSERVER_TITLE, tle, observer, sat)

			# Update before loop to prevent Live from showing an unpopulated layout
			screen.update_screen()

			if output_type == "rich":
				with Live(screen.layout, refresh_per_second=1, screen=True) as live:
					# Can only be interrupted by ctrl+C !
					while True:
						screen.update_screen()
						time.sleep(1.0)
			else:
				print_tle(tle)
				while True:
					screen.update_screen()
					time.sleep(1.0)

	except KeyboardInterrupt:
		pass
