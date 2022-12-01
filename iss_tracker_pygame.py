# iss_tracker_pygame.py
# Plot the path of the ISS on a map (rectilinear for simple x/y conversion)
# Also plot a list of lat/long places and indicate which is currently closest to the ISS
# Inspired by the NASA ISS Tracker: https://spotthestation.nasa.gov/tracking_map.cfm
# Map Image: NASA’s Terra satellite: https://commons.wikimedia.org/w/index.php?curid=50497070
# Space station icons created by monkik - Flaticon: https://www.flaticon.com/free-icons/space-station
#
# Martin Bridge, Aug 2021
#

# TODO: Optimise painting of elements. Paint all fixed elements on to background once

import math
import datetime
import time
import pygame
from pygame.locals import *
from skyfield.api import load, EarthSatellite
from get_tle import get_tle
from places import closest_place_to, latlong, places

SAT_NAME = "ISS (ZARYA)"
MAP_IMAGE = "Blue_Marble_2880px.png"
ICON_IMAGE = "space-station.png"
TITLE_FONT = "couriernewbold"
DATA_FONT = "calibribold"

# Geometry of UI components
icon_size = 50           # Assume square icon
icon_outer_size = 45     # Surrounding circle to highlight the satellite icon
icon_border_width = 3
icon_border_color = (0, 255, 0)
orbit_color_fwd = (200, 200, 200)
orbit_color_back = (255, 255, 100)
marker_color = (240, 55, 128)  # To plot cities/DCs

# TODO: Add scaling factor so all geometry scales with the main screen size
screen_scale = 1.0
# screen_w, screen_h = 1920, 1130              # Full Window (HD)
screen_w, screen_h = 1680, 1000              # Full Window (Mac)

# map_w, map_h = screen_w, 1080   # int(screen_w / 2)   # Equirectangular projection is 2:1
map_w, map_h = screen_w, 945    # int(screen_w / 2)   # Equirectangular projection is 2:1
map_x, map_y = 0, 100             # Offset of map relative to app screen

# Header across top of screen
header_w, header_h = 1920, 114
header_font_name = TITLE_FONT
header_font_size = 100
header_text_color = (255, 192, 0)
header_bg_color = (20, 20, 20)

# Data surface at bottom of screen
data_surface_w, data_surface_h = screen_w, 100
data_surface_color = (199, 70, 52)
# Labels
label_font_name = DATA_FONT
label_font_size = 30
label_color = (200, 200, 200)
# Data Fields
data_font_name = DATA_FONT
data_font_size = 36
data_color = "white"

# Time parameters for calculating observation time
actual_time_prev = time.time()               # Baseline time (actual real-world time)
app_time_prev = actual_time_prev             # Game/App time based on speed up / slow down within the app


class TextField:

	def __init__(self, surface, x, y, width, height, bg_color, text_color, font_name, font_size, text=""):
		self.surface = surface   # Surface on which this field is drawn
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.bg_color = bg_color
		self.text_color = text_color
		self.font_name = font_name
		self.font_size = font_size
		self.image = pygame.Surface([width, height])
		self.rect = self.image.get_rect()
		self.text = text
		self.font = pygame.font.SysFont(font_name, font_size)
		self.image.fill(bg_color)
		if text != "":
			self.write_text(text)
		return

	def write_text(self, text, centred=False):
		text_image = self.font.render(text, True, self.text_color, self.bg_color)

		bg_rect_x = self.x
		if centred:
			self.x = (self.surface.get_width() - text_image.get_width()) / 2
			bg_rect_x = (self.surface.get_width() - self.image.get_width()) / 2

		self.surface.blit(self.image, [bg_rect_x, self.y])
		self.surface.blit(text_image, [self.x, self.y])
		return


class DataSurface:

	def __init__(self, wd, ht, bg_color):
		self.width = wd
		self.height = ht
		self.color = bg_color
		self.surface = pygame.Surface([self.width, self.height])
		self.surface.fill(self.color)

		TextField(self.surface,     20, 15, 130, 50, bg_color, label_color, label_font_name, label_font_size, text="Latitude")
		TextField(self.surface,    150, 15, 130, 50, bg_color, label_color, label_font_name, label_font_size, text="Longitude")
		TextField(self.surface,    300, 15, 130, 50, bg_color, label_color, label_font_name, label_font_size, text="Altitude")
		TextField(self.surface,    460, 15, 200, 50, bg_color, label_color, label_font_name, label_font_size, text="Speed")
		TextField(self.surface,    670, 15, 350, 50, bg_color, label_color, label_font_name, label_font_size, text="Time (GMT)")
		TextField(self.surface,   1040, 15, 420, 50, bg_color, label_color, label_font_name, label_font_size, text="Nearest DC")
		TextField(self.surface, wd-160, 15, 150, 50, bg_color, label_color, label_font_name, label_font_size, text="Time Factor")

		self.lat_field        = TextField(self.surface,     20, 55, 130, 50, bg_color, data_color, data_font_name, data_font_size)
		self.long_field       = TextField(self.surface,    150, 55, 130, 50, bg_color, data_color, data_font_name, data_font_size)
		self.alt_field        = TextField(self.surface,    300, 55, 130, 50, bg_color, data_color, data_font_name, data_font_size)
		self.speed_field      = TextField(self.surface,    460, 55, 200, 50, bg_color, data_color, data_font_name, data_font_size)
		self.time_field       = TextField(self.surface,    670, 55, 350, 50, bg_color, data_color, data_font_name, data_font_size)
		self.dc_field         = TextField(self.surface,   1040, 55, 420, 50, bg_color, data_color, data_font_name, data_font_size)
		self.timefactor_field = TextField(self.surface, wd-160, 55, 150, 50, bg_color, data_color, data_font_name, data_font_size)

		return


# TODO: Separate classes for fixed part of Map (background + data center locations) from the dynamic part (satellite, orbits etc)
class Map:
	def __init__(self, sat, image_name, width, height):
		self.sat = sat
		self.width, self.height = width, height

		self.bg_image = pygame.image.load(image_name).convert()
		self.bg_image = pygame.transform.scale(self.bg_image, [width, height])
		# Plot fixed locations
		# Only locations with a GA data before today
		today = datetime.date.today().strftime("%Y-%m-%d")
		self.plot_all_dcs(on_date=today)

		self.surface = pygame.Surface([width, height])

		self.icon = pygame.image.load(ICON_IMAGE).convert_alpha()
		self.icon = pygame.transform.scale(self.icon, (icon_size, icon_size))

		return

	def update(self):
		# Repaint the image before redrawing all the elements (icon, track etc)
		self.surface.blit(self.bg_image, [0, 0])
		return

	def latlong_to_xy(self, lat, long):
		y = -int((lat / 180.0) * self.height - self.height / 2)
		x = int((long / 360.0) * self.width + self.width / 2)
		return x, y

	def draw_marker(self, lat, long):
		# Plot an X
		sz = 12  # Width of the X
		x, y = self.latlong_to_xy(lat, long)

		# Draw a circle
		pygame.draw.circle(self.bg_image, (255, 255, 255), [x, y], sz + 2, 3)
		pygame.draw.circle(self.bg_image, marker_color, [x, y], sz, 0)
		return

	def plot_sat(self, lat, long):
		x, y = self.latlong_to_xy(lat, long)

		# Draw circle, centred around icon
		pygame.draw.circle(self.surface, icon_border_color, [x, y], icon_outer_size, icon_border_width)

		# Draw icon (uses top-left coordinates)
		x = int(x - icon_size / 2)
		y = int(y - icon_size / 2)
		self.surface.blit(self.icon, [x, y])
		return

	def plot_all_dcs(self, on_date=""):
		# Only plot places with GA date before on_date
		for region in places:
			if region.ga_date < on_date:
				self.draw_marker(region.latlong.lat, region.latlong.lon)
		return

	def draw_line(self, from_lat, from_long, to_lat, to_long, color, lwidth):

		from_x, from_y = self.latlong_to_xy(from_lat, from_long)
		to_x, to_y = self.latlong_to_xy(to_lat, to_long)

		# Need to deal with lines that wrap around (i.e. cross the international date line)
		# If sat & city are in the quarter adjacent to the dateline (-180 to -90 or 90 to 180)
		# Two lines need to be drawn
		if abs(from_long - to_long) > 180:
			# Two lines required
			if from_x < to_x:
				x1 = to_x - screen_w
				x2 = from_x + screen_w
			else:
				x1 = to_x + screen_w
				x2 = from_x - screen_w

			pygame.draw.line(self.surface, color, [from_x, from_y], [x1, to_y], lwidth)
			pygame.draw.line(self.surface, color, [x2, from_y], [to_x, to_y], lwidth)
		else:
			pygame.draw.line(self.surface, color, [from_x, from_y], [to_x, to_y], lwidth)

	def draw_orbits(self, time_factor):

		# Plot orbit track +/- 90 mins, increments of 2 min
		increment_mins = 2
		orbit_plot_duration_mins = 90
		orbit_time_mins = -orbit_plot_duration_mins  # Start loop at preceding X minutes of orbit

		# Start plot 90 minutes in the past
		t_current = obs_time(time_factor)  # Get current time
		orbit_time = ts.utc(t_current.utc_datetime() + datetime.timedelta(minutes=orbit_time_mins))
		old_lat, old_long, alt, speed = get_sat_pos(self.sat, orbit_time)

		for orbit_time_mins in range(-orbit_plot_duration_mins, orbit_plot_duration_mins + increment_mins, increment_mins):

			orbit_time = ts.utc(t_current.utc_datetime() + datetime.timedelta(minutes=orbit_time_mins))

			orbit_lat, orbit_long, alt, speed = get_sat_pos(self.sat, orbit_time)

			if orbit_time_mins > 0:
				orbit_color = orbit_color_fwd
			else:
				orbit_color = orbit_color_back

			self.draw_line(orbit_lat, orbit_long, old_lat, old_long, orbit_color, 4)

			old_lat, old_long = orbit_lat, orbit_long
		return


class App:

	def __init__(self, sat):
		self.screen_w, self.screen_h = screen_w, screen_h
		self.map_w, self.map_h = map_w, map_h

		# TODO: Vary the max frame rate when the time factor changes
		self.max_frame_rate = 1
		self.time_factor = 1.0
		self.saved_time_factor = 1.0
		self.paused = False

		pygame.init()

		self.clock = pygame.time.Clock()
		self.main_screen = pygame.display.set_mode([self.screen_w, self.screen_h])  # flags=pygame.SCALED|pygame.RESIZABLE)
		pygame.display.set_caption("ISS Satellite Tracker, Oracle Cloud Regions")

		self.map = Map(sat, MAP_IMAGE, map_w, map_h)

		self.region_field = TextField(self.main_screen, int((screen_w - header_w) / 2), 0, header_w, 114,
		                              header_bg_color, header_text_color, header_font_name, header_font_size)

		self.data_surface = DataSurface(data_surface_w, data_surface_h, data_surface_color)

		self.sat = sat   # Satellite object for all orbit calculations

		return

	def update(self):
		# Background (map, whole screen) & data field surface (bottom of main screen)
		self.main_screen.blit(self.map.surface, [map_x, map_y])
		self.map.update()

		# Data surface at bottom of main window
		y = self.main_screen.get_height() - self.data_surface.height
		self.main_screen.blit(self.data_surface.surface, [0, y])
		return

	def run(self):

		global actual_time_prev, app_time_prev

		dead = False
		while not dead:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					dead = True
				if event.type == pygame.VIDEORESIZE:
					# There's some code to add back window content here.
					# old_surface_saved = self.main_screen
					self.main_screen = pygame.display.set_mode((event.w, event.h))
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE or event.key == K_q:  # Q/Esc = Quit
						dead = True
					elif event.key == K_p:  # P = Pause
						self.paused = not self.paused
						if self.paused:
							self.saved_time_factor = self.time_factor
							self.time_factor = 0
						else:
							self.time_factor = self.saved_time_factor
					elif event.key == K_EQUALS:  # + = speed up
						if -1.0 <= self.time_factor <= 0:
							self.time_factor = -self.time_factor
						elif self.time_factor > 0:
							self.time_factor *= 2
						else:
							self.time_factor /= 2
					elif event.key == K_MINUS:  # + = slow down
						# If slowing down below 1, then reverse time
						if 0 <= self.time_factor <= 1.0:
							self.time_factor = -self.time_factor
						elif self.time_factor < 0:
							self.time_factor *= 2
						else:
							self.time_factor /= 2
					elif event.key == K_1:  # Reset time factor to 1
						self.time_factor = 1
						self.saved_time_factor = 1
					elif event.key == K_r:  # R = Reset to real time now
						self.time_factor = 1
						app_time_prev = actual_time_prev

					if abs(self.time_factor) > 8:
						self.max_frame_rate = 20
					else:
						self.max_frame_rate = 1
			# Update background elements
			self.update()

			# Get sat time & data
			sat_time = obs_time(t_factor=self.time_factor)
			sat_lat, sat_long, alt, speed = get_sat_pos(self.sat, sat_time)

			# Plot satellite position and orbit lines
			self.map.plot_sat(sat_lat, sat_long)
			self.map.draw_orbits(self.time_factor)

			# Update data fields
			datetime_str = sat_time.tt_strftime("%d %b %Y, %H:%M:%S")
			lat_dir = "N" if sat_lat > 0 else "S"
			long_dir = "E" if sat_long > 0 else "W"

			# Find nearest DC
			today = datetime.date.today().strftime("%Y-%m-%d")
			nearest_city, dist = closest_place_to(latlong(sat_lat, sat_long), today)
			region_name = nearest_city.id
			region_loc = nearest_city.latlong

			self.data_surface.lat_field.write_text(f"{abs(sat_lat):3.1f} {lat_dir}")
			self.data_surface.long_field.write_text(f"{abs(sat_long):3.1f} {long_dir}")
			self.data_surface.alt_field.write_text(f"{alt:3.0f} km")
			self.data_surface.speed_field.write_text(f"{speed:.0f} km/h")
			self.data_surface.time_field.write_text(datetime_str)
			self.data_surface.timefactor_field.write_text(f"{self.time_factor:-.1f}")
			self.data_surface.dc_field.write_text(f"{region_name} ({dist:.0f}km)")

			# Display name of nearest region & draw line from sat to nearest location
			self.region_field.write_text(f" {region_name} ", centred=True)
			self.map.draw_line(sat_lat, sat_long, region_loc.lat, region_loc.lon, icon_border_color, 4)

			pygame.display.flip()
			self.clock.tick(self.max_frame_rate)

		pygame.quit()

		return


def obs_time(t_factor=1.0):
	global actual_time_prev, app_time_prev
	# Get datetime of observation as a timescale object
	# Speed up time by a time factor
	# t denotes system time, gt denotes (accelerated) game time

	t_now = time.time()                           # Actual time now
	t_step = (t_now - actual_time_prev)           # Time since last update
	app_time_step = t_step * t_factor             # Accelerated time since last update

	app_time_now = app_time_prev + app_time_step  # New accelerated time
	gmt = time.gmtime(app_time_now)               # GMT for input to skyfield observation time

	actual_time_prev = t_now
	app_time_prev = app_time_now

	# print(f"t_now={t_now:12.2f}  t_step={t_step:6.5f}    gt1={gt1:12.2f}  app_time_step={app_time_step:6.5f}  gmt={gmt}")
	t = ts.utc(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, gmt.tm_sec)
	return t


def get_sat_pos(sat, sat_time):

	geocentric = sat.at(sat_time)
	subpoint = geocentric.subpoint()

	dlat = subpoint.latitude.degrees
	dlon = subpoint.longitude.degrees
	elev = subpoint.elevation.km

	# Velocity from 3D vector
	vel_km_s = math.sqrt(
				geocentric.velocity.km_per_s[0]**2
				+ geocentric.velocity.km_per_s[1]**2
				+ geocentric.velocity.km_per_s[2]**2)

	# return velocity in km/h
	return dlat, dlon, elev, vel_km_s * 3600


if __name__ == "__main__":

	found, tle_line1, tle_line2 = get_tle(SAT_NAME)

	if found:
		ts = load.timescale()
		satellite = EarthSatellite(tle_line1, tle_line2, SAT_NAME, ts)
		app = App(satellite)
		app.run()
	else:
		print(f"Satellite {SAT_NAME} not found")
