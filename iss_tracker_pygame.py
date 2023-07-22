# iss_tracker_pygame.py
# Plot the path of the ISS on a map (Equirectangular for simple x/y conversion)
# Also plot a list of lat/long places and indicate which is currently closest to the ISS
# Inspired by the NASA ISS Tracker: https://spotthestation.nasa.gov/tracking_map.cfm
# Map Image: NASA’s Terra satellite: https://commons.wikimedia.org/w/index.php?curid=50497070
# Space station icons created by monkik - Flaticon: https://www.flaticon.com/free-icons/space-station
#
# Martin Bridge, Aug 2021
# 14-jan-2023   mbridge     Added scaling using window size as a command line parameter
# 17-jan-2023   mbridge     Added day/night and solar subpoint to map
# 01-feb-2023   mbridge     Parameters for window width & full screen

import argparse
import math
import datetime
import time
import pygame
from pygame.locals import *
from skyfield import almanac
from skyfield.api import load, EarthSatellite, wgs84
import skyfield.positionlib
from get_tle import get_tle
from places import closest_place_to, latlong, places

DEBUG = False       # Global - switched on with keystroke
first_obs_time = True   # Allows setting initial date/time

DAY_IMAGE = 'earth_day_lrg.jpg'
NIGHT_IMAGE = 'earth_night_lrg.jpg'
DISPLAY_NIGHT = True

ISS_IMAGE = "space-station.png"
SUN_IMAGE = "sun-4-xxl.png"

# Geometry of UI components
icon_size = 50  # Assume square icon
icon_outer_size = 45  # Surrounding circle to highlight the satellite icon
icon_border_width = 3
icon_border_color = (0, 255, 0)
orbit_color_back = (200, 200, 200)
orbit_color_fwd = (255, 255, 100)
marker_color = (240, 55, 128)  # To plot cities/DCs
marker_outline = (255, 255, 255)

# base values are what were used to calculate original layout on an HD screen
base_w, base_h = 1920, 1080


# Screen layout before scaling
# Overall screen = 1920 x 1080
# +--------------------------------------------+
# |            Header (1920 x 100)             |
# +--------------------------------------------+
# |                                            |
# |                                            |
# |           Map image 1920 x 960             |
# |            Map view 1920 x 880             |
# |                                            |
# +--------------------------------------------+
# |          Data Surface (1920 x 100)         |
# +--------------------------------------------+

header_w = base_w
header_h = 100         # Header across top of screen
header_color = (32, 32, 32)
base_map_w = base_w
base_map_h = 880       # Was 945
data_surface_w = base_w
data_surface_h = 100
data_surface_color = (199, 70, 52)     # Data surface at bottom of screen
header_font = {'name': 'couriernew', 'size': 48, 'bold': True,  'color': (255, 192, 0),   'bg_color': header_color}
label_font = {'name': 'calibri',    'size': 30, 'bold': False, 'color': (200, 200, 200), 'bg_color': data_surface_color}
data_font = {'name': 'calibri',    'size': 36, 'bold': False, 'color': "white",         'bg_color': data_surface_color}

# # Time parameters for calculating observation time
# actual_time_prev = time.time()  # Baseline time (actual real-world time)
# # app_time_prev = actual_time_prev  # Game/App time based on speed up / slow down within the app

# Constants
two_pi = 2 * math.pi
pi_over_180 = math.pi / 180.0
one_eighty_over_pi = 180.0 / math.pi


class TextField:

    def __init__(self, surface, x, y, width, height, screen_scale, font, text=""):

        self.surface = surface  # Surface on which this field is drawn
        self.x = int(x * screen_scale)
        self.y = int(y * screen_scale)
        self.width = int(width * screen_scale)
        self.height = int(height * screen_scale)
        self.bg_color = font['bg_color']
        self.text_color = font['color']
        self.font_name = font['name']
        self.font_size = int(font['size'] * screen_scale)
        self.bold = font['bold']

        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.text = text
        self.font = pygame.font.SysFont(self.font_name, self.font_size, bold=self.bold)

        font_h = self.font.get_height()

        self.image.fill(self.bg_color)
        if text != "":
            self.write_text(text)
        return

    def write_text(self, text, centered=False, vcentered=False):
        text_image = self.font.render(text, True, self.text_color, self.bg_color)

        bg_rect_x = self.x
        bg_rect_y = self.y
        if centered:
            self.x = (self.surface.get_width() - text_image.get_width()) / 2
            bg_rect_x = (self.surface.get_width() - self.image.get_width()) / 2

        if vcentered:
            self.y = (self.surface.get_height() - text_image.get_height()) / 2
            bg_rect_y = (self.surface.get_height() - self.image.get_height()) / 2

        self.surface.blit(self.image, [bg_rect_x, bg_rect_y])
        self.surface.blit(text_image, [self.x, self.y])
        return


class HeaderSurface:

    def __init__(self, wd, ht, screen_scale, bg_color):
        self.screen_scale = screen_scale
        self.width = int(wd * screen_scale)
        self.height = int(ht * screen_scale)
        self.color = bg_color
        self.surface = pygame.Surface([self.width, self.height])
        self.surface.fill(self.color)

        self.heading_field = TextField(self.surface, 0, 0, wd, ht, screen_scale, header_font)

        return


class DataSurface:

    def __init__(self, wd, ht, screen_scale, bg_color):
        self.screen_scale = screen_scale
        self.width = int(wd * screen_scale)
        self.height = int(ht * screen_scale)
        self.color = bg_color
        self.surface = pygame.Surface([self.width, self.height])
        self.surface.fill(self.color)

        TextField(self.surface,  20, 15, 130, 50, screen_scale, label_font, text="Latitude")
        TextField(self.surface, 150, 15, 130, 50, screen_scale, label_font, text="Longitude")
        TextField(self.surface, 300, 15, 130, 50, screen_scale, label_font, text="Altitude")
        TextField(self.surface, 440, 15, 200, 50, screen_scale, label_font, text="Speed")
        TextField(self.surface, 660, 15, 350, 50, screen_scale, label_font, text="Time (GMT)")
        TextField(self.surface, 1015, 15, 420, 50, screen_scale, label_font, text="Nearest Place")
        TextField(self.surface, 1700, 15, 150, 50, screen_scale, label_font, text="Time Factor")

        self.lat_field = TextField(self.surface, 20, 55, 130, 50, screen_scale, data_font)
        self.long_field = TextField(self.surface, 150, 55, 130, 50, screen_scale, data_font)
        self.alt_field = TextField(self.surface, 300, 55, 130, 50, screen_scale, data_font)
        self.speed_field = TextField(self.surface, 440, 55, 200, 50, screen_scale, data_font)
        self.time_field = TextField(self.surface, 660, 55, 350, 50, screen_scale, data_font)
        self.place_field = TextField(self.surface, 1015, 55, 680, 50, screen_scale, data_font)
        self.timefactor_field = TextField(self.surface, 1700, 55, 150, 50, screen_scale, data_font)

        return


class Map:

    def __init__(self, sat, timescale, day_image_name, night_image_name, width, height, screen_scale):
        self.sat = sat
        self.ts = timescale

        self.screen_scale = screen_scale
        self.width = int(width * self.screen_scale)
        self.height = int(height * self.screen_scale)

        self.surface = pygame.Surface([self.width, self.height])

        # For the fixed parts of the display (places, tropics, maps)
        self.drawing_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        # self.drawing_layer = self.drawing_layer.convert_alpha()

        self.day_image = pygame.image.load(day_image_name).convert()
        self.day_image = pygame.transform.scale(self.day_image, [self.width, self.height])
        # self.night_image = pygame.image.load(night_image_name).convert()
        # self.night_image = pygame.transform.scale(self.night_image, [self.width, self.height])

        # To draw the night shading
        self.mask = pygame.Surface([self.width, self.height])

        # Plot fixed locations defined before given start date (today)
        today = datetime.date.today()
        datestr = today.strftime("%Y-%m-%d")
        self.plot_all_places(on_date=datestr)

        icon_size_scaled = int(icon_size * self.screen_scale)

        self.iss_icon = pygame.image.load(ISS_IMAGE).convert_alpha()
        self.iss_icon = pygame.transform.scale(self.iss_icon, (icon_size_scaled, icon_size_scaled))

        self.sun_icon = pygame.image.load(SUN_IMAGE).convert_alpha()
        self.sun_icon = pygame.transform.scale(self.sun_icon, (icon_size_scaled, icon_size_scaled))

        self.ephemeris = load('de421.bsp')      # For Sun calculations

        year = today.year
        self.vernal, self.autumnal = self.get_equinoxes(year)

        return

    def update(self):
        # Repaint the image before redrawing all the elements (icon, track etc)

        # Update day/night mask
        # self.surface.blit(self.night_image, [0, 0])
        self.surface.blit(self.day_image, [0, 0])
        self.surface.blit(self.mask, [0, 0])
        self.surface.blit(self.drawing_layer, [0, 0])

        return

    def draw_tropics(self):
        eq_color = (128, 128, 128)    # Equator
        t_color = (64, 64, 64)       # Tropics
        t_polar = (64, 64, 255)

        # Equator
        pygame.draw.line(self.drawing_layer, eq_color, (0, self.height/2), (self.width, self.height/2), 2)
        # Cancer
        x, y = self.latlong_to_xy(23.44, 0)
        pygame.draw.line(self.drawing_layer, t_color, (0, y), (self.width, y), 1)
        # Capricorn
        x, y = self.latlong_to_xy(-23.44, 0)
        pygame.draw.line(self.drawing_layer, t_color, (0, y), (self.width, y), 1)
        # Arctic
        x, y = self.latlong_to_xy(66.536, 0)
        pygame.draw.line(self.drawing_layer, t_polar, (0, y), (self.width, y), 1)
        # Antarctic
        x, y = self.latlong_to_xy(-66.536, 0)
        pygame.draw.line(self.drawing_layer, t_polar, (0, y), (self.width, y), 1)

    def draw_marker(self, lat, long):

        # Plot a marker
        radius = int(6 * self.screen_scale)  # Width of the X
        line_width = int(2 * self.screen_scale)
        x, y = self.latlong_to_xy(lat, long)

        # Draw a circle
        pygame.draw.circle(self.drawing_layer, marker_outline, [x, y], radius + line_width, line_width)
        pygame.draw.circle(self.drawing_layer, marker_color, [x, y], radius, 0)
        return

    def plot_sat(self, lat, long):

        x, y = self.latlong_to_xy(lat, long)

        # Draw circle, centred around icon
        pygame.draw.circle(self.surface, icon_border_color, [x, y], int(icon_outer_size * self.screen_scale),
                           int(icon_border_width * self.screen_scale))

        # Draw icon (uses top-left coordinates)
        offset = self.iss_icon.get_width() / 2
        x = int(x - offset)
        y = int(y - offset)

        self.surface.blit(self.iss_icon, [x, y])

        return

    def plot_all_places(self, on_date=""):
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
                x1 = to_x - self.width
                x2 = from_x + self.width
            else:
                x1 = to_x + self.width
                x2 = from_x - self.width

            pygame.draw.line(self.surface, color, [from_x, from_y], [x1, to_y], lwidth)
            pygame.draw.line(self.surface, color, [x2, from_y], [to_x, to_y], lwidth)
        else:
            pygame.draw.line(self.surface, color, [from_x, from_y], [to_x, to_y], lwidth)

    def latlong_to_xy(self, lat, long):
        y = -int(((lat / 180.0) * self.height) - self.height / 2)
        x = int(((long / 360.0) * self.width) + self.width / 2)
        return x, y

    def xy_to_latlong(self, x, y):
        lat = (360.0 * x / self.width) - 180.0
        long = 90 - (180.0 * y / self.height)
        return lat, long

    # Get Vernal and Autumnal Equinoxes to determine how to draw day/night
    def get_equinoxes(self, year):
        # Get seasons for current year
        t0 = self.ts.utc(year, 1, 1)
        t1 = self.ts.utc(year, 12, 31)
        t, y = almanac.find_discrete(t0, t1, almanac.seasons(self.ephemeris))

        for yi, ti in zip(y, t):
            print(yi, almanac.SEASON_EVENTS[yi], ti.utc_iso(' '))

        return t[0], t[2]

    def draw_night(self, time_factor):

        t_current = obs_time(self.ts, time_factor)  # Get current time

        # Make a semi transparent surface
        mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        mask_color = (0, 0, 0, 100)

        # Loading the position of the Sun
        sun_from_earth = self.ephemeris['earth'].at(t_current).observe(self.ephemeris['sun'])
        ra, dec, distance = sun_from_earth.radec()

        earth = 399
        sun = skyfield.positionlib.position_of_radec(ra.hours, dec.degrees, t=t_current, center=earth)
        sun_subpoint = wgs84.subpoint(sun)

        sun_long_deg = sun_subpoint.longitude.degrees
        sun_lat_deg = sun_subpoint.latitude.degrees

        sun_x, sun_y = self.latlong_to_xy(sun_lat_deg, sun_long_deg)

        # Draw icon (uses top-left coordinates)
        offset = self.sun_icon.get_width() / 2
        sun_x = int(sun_x - offset)
        sun_y = int(sun_y - offset)

        # TODO: Optimise by only drawing a new map if day changes, otherwise just shift mask left
        # TODO: Allow for a mask which reveals underlying night image
        # if DISPLAY_NIGHT:
        #     day2 = self.map.day_image.copy()
        #     black = (0, 0, 0)
        #     day2.set_colorkey(black)
        #     self.mask = self.map.draw_day_night(self.time_factor)
        #     day2.blit(self.mask, (0, 0))

        old_x, old_y = -1, -1  # dummy start
        old_y2 = -1
        x, y, y2 = 0, 0, 0

        nsteps = 120
        step = int(self.width / nsteps)

        for x in range(0, self.width + step, step):
            long_degrees = ((360.0 * x / self.width) - 180.0)
            lat_degrees, test_dec = self.terminator(long_degrees, t_current)
            # lat_degrees_2, test_dec_2 = self.terminator2(long_degrees, t_current)

            # Shading of terminator line goes down when declination is > 0, otherwise up
            end_y = self.height if test_dec > 0 else 0
            # end_y2 = self.height if test_dec_2 > 0 else 0

            y = -int(((lat_degrees / 180.0) * self.height) - self.height / 2)
            # y2 = -int(((lat_degrees_2 / 180.0) * self.height) - self.height / 2)

            if old_x == -1:  # First time in loop
                old_x = x
                old_y = y
                old_y2 = y2
            else:
                # Draw the terminator (the day/night line, useful when testing)

                # pygame.draw.line(mask, (0, 255, 0), (old_x, old_y), (x, y), width=5)
                pygame.draw.polygon(mask, mask_color, ((old_x, old_y), (x, y), (x, end_y), (old_x, end_y)), 0)

                # pygame.draw.line(mask, (255, 255, 0), (old_x, old_y2), (x, y2), width=5)
                # pygame.draw.polygon(mask, mask_color, ((old_x, old_y2), (x, y2), (x, end_y2), (old_x, end_y2)), 0)

                old_x = x
                old_y = y
                old_y2 = y2

        mask.blit(self.sun_icon, [sun_x, sun_y])

        return mask

    # Calculate latitude of the day/night terminator line for given longiture & time of day
    def terminator(self, long_degrees, t_current):
        # Calculations from https://github.com/marmat/google-maps-api-addons

        max_declination = 23.44 * pi_over_180
        tm = t_current.utc_datetime().timetuple()

        day_secs = tm.tm_hour * 3600 + tm.tm_min * 60 + tm.tm_sec
        fraction_of_day = day_secs / 86400
        time_offset = two_pi * (0.5 + fraction_of_day)

        declination = math.sin(two_pi * (t_current.ut1 - self.vernal.ut1) / 365) * max_declination
        long = long_degrees * pi_over_180

        # Avoid divide by zero when declination is zero
        if abs(t_current.ut1 - self.vernal.ut1) < 1 / 86400000:  # or declination2 == 0:
            lat_degrees = 0
        else:
            lat_degrees = math.atan(-math.cos(long + time_offset) / math.tan(declination)) * one_eighty_over_pi

        # if long_degrees == 0:
        #     print(f"T1:  {t_current} :  long: {long:10.6f}  frac: {fraction_of_day:11.3f}  "
        #           f"time_offset: {time_offset:10.8f}  dec: {declination:10.6f}  "
        #           f"dec.degrees: {declination*one_eighty_over_pii}  lat:{lat_degrees:6.4f} "
        #           f"dec3: {declination:18.16f}")

        return lat_degrees, declination

    def terminator2(self, long_degrees, t_current):
        sun_from_earth = self.ephemeris['earth'].at(t_current).observe(self.ephemeris['sun'])

        ra, dec, distance = sun_from_earth.radec()
        declination = dec.degrees * pi_over_180
        long = long_degrees * pi_over_180
        day_secs = t_current.utc.hour * 3600 + t_current.utc.minute * 60 + t_current.utc.second
        fraction_of_day = day_secs / 86400
        time_offset = two_pi * (0.5 + fraction_of_day)

        lat_degrees = math.atan(-math.cos(long + time_offset) / math.tan(declination)) * one_eighty_over_pi

        # if long_degrees == 0:
        #     print(f"T2:  {t_current} :  long: {long:10.6f}  frac: {fraction_of_day:11.3f}  "
        #           f"time_offset: {time_offset:10.8f}  dec: {declination:10.6f}  "
        #           f"dec.degrees: {dec.degrees}  lat:{lat_degrees:6.4f}")

        return lat_degrees, declination

    def draw_orbits(self, time_factor):

        # Plot orbit track +/- 90 mins, increments of 2 min
        increment_mins = 2
        orbit_duration_mins = 90
        orbit_time_mins = -orbit_duration_mins  # Start loop at preceding X minutes of orbit

        # Start plot 90 minutes in the past
        t_current = obs_time(self.ts, time_factor)  # Get current time
        # TODO change to UT1
        orbit_time = self.ts.utc(t_current.utc_datetime() + datetime.timedelta(minutes=orbit_time_mins))
        old_lat, old_long, alt, speed = get_sat_pos(self.sat, orbit_time)

        for orbit_time_mins in range(-orbit_duration_mins, orbit_duration_mins + increment_mins, increment_mins):

            orbit_time = self.ts.utc(t_current.utc_datetime() + datetime.timedelta(minutes=orbit_time_mins))

            orbit_lat, orbit_long, alt, speed = get_sat_pos(self.sat, orbit_time)

            if orbit_time_mins > 0:
                orbit_color = orbit_color_fwd
            else:
                orbit_color = orbit_color_back

            self.draw_line(orbit_lat, orbit_long, old_lat, old_long, orbit_color, 4)

            old_lat, old_long = orbit_lat, orbit_long

        return


class App:

    def __init__(self, sat_name, screen_w, screen_h, start_at, fullscreen=False):

        # self.sat = sat  # Satellite object for all orbit calculations

        self.ts = load.timescale()
        self.sat = EarthSatellite(tle_line1, tle_line2, sat_name, self.ts)
        self.start_at = start_at

        self.screen_w, self.screen_h = screen_w, screen_h
        self.screen_scale = float(screen_w / base_w)
        print(f"Scale: {self.screen_scale}")

        self.map_w = base_map_w
        self.map_h = base_map_h
        self.map_x = 0

        # Map starts immediately below header, also truncated
        self.map_y = int(header_h * self.screen_scale)
        # self.map_y = int((base_h - base_map_h)/2)

        self.max_frame_rate = 20
        self.time_factor = 1.0
        self.saved_time_factor = 1.0
        self.paused = False

        pygame.init()
        self.clock = pygame.time.Clock()
        self.main_surface = pygame.Surface([self.screen_w, self.screen_h])

        options = pygame.FULLSCREEN + pygame.SCALED if fullscreen else 0
        # options = options + pygame.SCALED
        self.main_screen = pygame.display.set_mode([self.screen_w, self.screen_h], options)
        pygame.display.set_caption("Satellite Tracker")

        self.map = Map(self.sat, self.ts, DAY_IMAGE, NIGHT_IMAGE, self.map_w, self.map_h, self.screen_scale)

        # Heading field centered
        self.header_surface = HeaderSurface(header_w, header_h, self.screen_scale, header_color)
        self.data_surface = DataSurface(data_surface_w, data_surface_h, self.screen_scale, data_surface_color)

        pygame.event.set_allowed([QUIT, KEYDOWN])

        return

    def resize_screen(self, new_width, new_height):
        pygame.display.set_mode([new_width, new_height])
        new_surface = pygame.Surface([new_width, new_height])
        pygame.transform.scale(self.main_surface, [new_width, new_height], new_surface)

        self.main_surface = new_surface
        pass

    def update(self):
        # Background (map, whole screen) & data field surface (bottom of main screen)
        self.main_surface.blit(self.map.surface, [self.map_x, self.map_y])
        self.map.update()

        # Header at top of main window
        self.main_surface.blit(self.header_surface.surface, [0, 0])

        # Data surface at bottom of main window
        data_surface_y = self.main_screen.get_height() - self.data_surface.height
        self.main_surface.blit(self.data_surface.surface, [0, data_surface_y])
        self.main_screen.blit(self.main_surface, [0, 0])

        return

    def run(self):

        global actual_time_prev, app_time_prev, DISPLAY_NIGHT

        if self.start_at is not None:
            # Start time specified on command line
            tm_start = time.mktime(time.strptime(start_at, "%Y-%m-%d %H:%M:%S"))
            actual_time_prev = tm_start
        else:
            # Otherwise start from now
            actual_time_prev = time.time()
        # App time = actual time as no speed up applied at start of program
        app_time_prev = actual_time_prev  # Game/App time based on speed up / slow down within the app

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    # There's some code to add back window content here.
                    # old_surface_saved = self.main_screen
                    self.main_screen = pygame.display.set_mode((event.w, event.h))
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_q:  # Q/Esc = Quit
                        running = False
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
                    elif event.key == K_n:  # Day Night Mask
                        DISPLAY_NIGHT = not DISPLAY_NIGHT
                    # Increase the max frame rate when the time factor speeds up (crude!)
                    if abs(self.time_factor) >= 8:
                        self.max_frame_rate = 40
                    else:
                        self.max_frame_rate = 1


            # Get sat time & data
            sat_time = obs_time(self.ts, t_factor=self.time_factor)
            sat_lat, sat_long, alt, speed = get_sat_pos(self.sat, sat_time)

            # Update data fields
            datetime_str = sat_time.utc_strftime("%d %b %Y, %H:%M:%S")
            lat_dir = "N" if sat_lat > 0 else "S"
            long_dir = "E" if sat_long > 0 else "W"

            # Find the closest place
            valid_when = sat_time.utc_strftime("%Y-%m-%d")
            closest_place, dist = closest_place_to(latlong(sat_lat, sat_long), valid_when)
            place_id = closest_place.id
            place_name = closest_place.name
            place_loc = closest_place.latlong

            self.data_surface.lat_field.write_text(f"{abs(sat_lat):3.1f} {lat_dir}")
            self.data_surface.long_field.write_text(f"{abs(sat_long):3.1f} {long_dir}")
            self.data_surface.alt_field.write_text(f"{alt:3.0f} km")
            self.data_surface.speed_field.write_text(f"{speed:.0f} km/h")
            self.data_surface.time_field.write_text(datetime_str)
            self.data_surface.timefactor_field.write_text(f"{self.time_factor:-.1f}")
            self.data_surface.place_field.write_text(f"{place_id} ({dist:.0f}km)")

            # Display name of the closes place & draw line from sat to that location
            self.header_surface.heading_field.write_text(f" {place_id}, {place_name} ", centered=True, vcentered=True)
            self.map.draw_line(sat_lat, sat_long, place_loc.lat, place_loc.lon, icon_border_color, 4)

            # Plot satellite position and orbit lines
            self.map.draw_orbits(self.time_factor)
            self.map.plot_sat(sat_lat, sat_long)
            if DISPLAY_NIGHT:
                self.map.mask = self.map.draw_night(self.time_factor)
            else:
                self.map.mask = pygame.Surface([1,1])

            self.clock.tick(self.max_frame_rate)
            pygame.display.flip()
            # Update background elements
            self.update()

        pygame.quit()

        return


# Get datetime of observation as a timescale object (Speed up time by a time factor)
def obs_time(ts, t_factor=1.0):
    global actual_time_prev, app_time_prev, first_obs_time

    t_now = time.time()  # Actual time now
    if first_obs_time:
        app_time_now = app_time_prev
        first_obs_time = False
    else:
        t_step = (t_now - actual_time_prev)  # Time since last update
        app_time_step = t_step * t_factor  # Accelerated time since last update
        app_time_now = app_time_prev + app_time_step  # New accelerated time

    gmt = time.gmtime(app_time_now)  # GMT for input to skyfield observation time

    actual_time_prev = t_now
    app_time_prev = app_time_now

    t = ts.ut1(gmt.tm_year, gmt.tm_mon, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, gmt.tm_sec)

    return t


def get_sat_pos(sat, sat_time):
    geocentric = sat.at(sat_time)
    subpoint = geocentric.subpoint()

    dlat = subpoint.latitude.degrees
    dlon = subpoint.longitude.degrees
    elev = subpoint.elevation.km

    # Velocity from 3D vector
    vel_km_s = math.sqrt(
        geocentric.velocity.km_per_s[0] ** 2
        + geocentric.velocity.km_per_s[1] ** 2
        + geocentric.velocity.km_per_s[2] ** 2)

    # return velocity in km/h
    return dlat, dlon, elev, vel_km_s * 3600


def get_screen_size():
    pygame.init()
    screen = pygame.display.set_mode()
    w, h = screen.get_size()
    pygame.display.quit()
    return w, h


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='ISS Tracker')

    parser.add_argument('-d', '--debug', help="Debug output", required=False, default=False, action="store_true")
    parser.add_argument('-s', '--satellite_name', help="Name of Satellite", required=False, default="ISS (ZARYA)")
    parser.add_argument('-a', '--start_at', help="Starting date/time (YYYY-MM-DD hh:mm:ss)", required=False)
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument('-f', '--fullscreen', help="Run full screen (window size parameters ignored)",
                            required=False, default=False, action="store_true")
    size_group.add_argument('-w', '--window_width', help=f'Window Width -[{base_w}]', type=int, default=base_w)
    parser.add_argument('-t', '--tropics', help="Draw tropics ", required=False, default=False, action="store_true")

    args = parser.parse_args()
    DEBUG = args.debug
    sat_name = args.satellite_name
    start_at = args.start_at
    fullscreen = args.fullscreen
    draw_tropics = args.tropics

    if fullscreen:
        mon_w, mon_h = get_screen_size()
        full_screen_w = int(base_w * mon_h / base_h)
        win_w = full_screen_w
        win_h = mon_h
    elif args.window_width:
        win_w = int(args.window_width)
        win_h = base_h * (win_w / base_w)

    found, tle_line1, tle_line2 = get_tle(sat_name)

    if found:
        app = App(sat_name, win_w, win_h, start_at, fullscreen=fullscreen)

        if draw_tropics:
            app.map.draw_tropics()
        app.run()
    else:
        print(f"Satellite {sat_name} not found")
