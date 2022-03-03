# Given a lat/long, find the nearest place from the list 

import math
from collections import namedtuple
from datetime import date

latlong = namedtuple("Coords", ['lat', 'lon'])
place = namedtuple("Location", ['id', 'name', 'latlong', 'ga_date'])

# Places are any lat/long position, the following are the locations of Oracle's cloud regions
# Only places that have a ga_date in the past are considered
# OCI Regions from https://docs.cloud.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
places = [
	place('us-phoenix-1', 'Phoenix', latlong(33.45, -112.066667), '2016-10-20'),
	place('us-ashburn-1', 'Ashburn', latlong(39.043611, -77.4875), '2017-05-15'),
	place('eu-frankfurt-1', 'Frankfurt', latlong(50.110884, 8.6794922), '2017-09-29'),
	place('uk-london-1', 'London', latlong(51.5001524, -0.1262362), '2018-03-19'),
	place('ca-toronto-1', 'Toronto', latlong(43.6518927, -79.381713), '2019-01-17'),
	place('ap-tokyo-1', 'Tokyo', latlong(35.683333, 139.766667), '2019-04-30'),
	place('ap-seoul-1', 'Seoul', latlong(37.56, 126.99), '2019-05-13'),
	place('ap-mumbai-1', 'Mumbai', latlong(18.975, 72.825833), '2019-07-26'),
	place('eu-zurich-1', 'Zurich', latlong(47.366667, 8.55), '2019-08-09'),
	place('sa-saopaulo-1', 'Sao Paulo', latlong(-23.5486657, -46.6382522), '2019-08-23'),
	place('ap-sydney-1', 'Sydney', latlong(-33.8727635, 151.2053446), '2019-08-30'),
	place('ap-osaka-1', 'Osaka', latlong(34.693889, 135.502222), '2020-01-24'),
	place('ap-melbourne-1', 'Melbourne', latlong(-37.813611, 144.963056), '2020-02-01'),
	place('eu-amsterdam-1', 'Amsterdam', latlong(52.3731663, 4.8906596), '2020-02-01'),
	place('me-jeddah-1', 'Jeddah', latlong(21.543333, 39.172778), '2020-02-01'),
	place('ca-montreal-1', 'Montreal', latlong(45.509062, -73.553363), '2020-03-01'),
	place('ap-hyderabad-1', 'Hyderabad', latlong(17.366, 78.476), '2020-04-30'),
	place('ap-chuncheon-1', 'Chuncheon', latlong(37.8696345, 127.7386813), '2020-05-29'),
	place('us-sanjose-1', 'San Jose', latlong(37.333333, -121.9), '2020-07-24'),
	place('me-dubai-1', 'Dubai', latlong(25.026, 55.185), '2020-09-30'),
	place('uk-cardiff-1', 'Newport', latlong(51.4813069, -3.1804979), '2020-10-30'),
	place('sa-santiago-1', 'Santiago', latlong(-33.45, -70.666667), '2020-11-30'),
	place('sa-vinhedo-1', 'Vinhedo', latlong(-23.0395987, -46.9845879), '2021-05-28'),
	place('il-jerusalem-1', 'Jerusalem', latlong(31.8024155, 35.207303), '2021-10-10'),
	place('me-abudhabi-1', 'Abu Dhabi', latlong(24.4881757, 54.3549462), '2021-10-31'),
	place('ap-singapore-1', 'Singapore', latlong(1.2925, 103.8022), '2021-10-31'),
	place('eu-marseille-1', 'Marseille', latlong(43.321, 5.386), '2021-10-31'),
	place('eu-stockhom-1', 'Stockholm', latlong(59.329444, 18.068611), '2021-12-17'),
	place('eu-milan-1', 'Milan', latlong(45.4636183, 9.1881156), '2021-11-20'),
	place('af-johannesburg-1', 'Johannesburg', latlong(-26.201452, 28.045488), '2022-01-08'),
	place('eu-paris-1', 'Paris', latlong(48.856895, 2.3508487), '2022-02-28'),
	place('eu-madrid-1', 'Madrid', latlong(40.4167, -3.7003), '2022-03-09'),
	place('mx-queretaro-1', 'Queretaro', latlong(20.5875, -100.392778), '2099-01-01')
]

R = 6371.0     # Radius of Earth (km)


def dist_between(p1, p2):
	# Haversine method for great circle distance
	lat1 = math.radians(p1.lat)
	lon1 = math.radians(p1.lon)
	lat2 = math.radians(p2.lat)
	lon2 = math.radians(p2.lon)

	# Difference
	dlat = lat1 - lat2
	dlon = lon1 - lon2

	a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	distance = R * c

	return distance


def closest_place_to(location, on_date=''):
	# Only check places with ga_date before the given date or today
	# Optional: on-date
	if on_date == '':
		on_date = date.today().strftime("%Y-%d-%d")
	closest_dist = 99999
	closest_place = 'NOTFOUND'

	for r in [p for p in places if p.ga_date < on_date]:
		d = dist_between(r.latlong, location)

		if d < closest_dist:
			closest_dist = d
			closest_place = r

	return closest_place, closest_dist


# Main for testing only
if __name__ == '__main__':
	t_city, t_dist = closest_place_to(latlong(55, 0))
	print(f"Closest place is {t_city} ({t_dist:.0f} km)")
