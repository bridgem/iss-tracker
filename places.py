# Given a lat/long, find the nearest place from the list 

import math
from collections import namedtuple
from datetime import date
import csv

latlong = namedtuple('Latlong', ['lat', 'lon'])
place = namedtuple('Place', ['id', 'name', 'latlong', 'valid_from'])


# EXPERIMENTAL: named lists
place_list = namedtuple('Placelist', ['Listname', 'plist'])

dict1 = {'title': 'Olympics',
         'places': [
             place('Athens', 'Summer 1896,2004', latlong(37.9839412, 23.7283052), '6/4/1896'),
             place('Paris', 'Summer 1900,1924,2024', latlong(48.8534951, 2.3483915), '1900-05-14'),
         ]}

list1 = place_list('Olympics', [
            place('Athens', 'Summer 1896,2004', latlong(37.9839412, 23.7283052), '6/4/1896'),
            place('Paris', 'Summer 1900,1924,2024', latlong(48.8534951, 2.3483915), '1900-05-14')
])

list2 = place_list('OCI', [
    place('us-phoenix-1', 'Phoenix', latlong(33.45, -112.066667), '2016-10-20'),
    place('us-ashburn-1', 'Ashburn', latlong(39.043611, -77.4875), '2017-05-15'),
])

list3 = list1
list1[1].append(place('ap-tokyo-1', 'Tokyo', latlong(35.683333, 139.766667), '2019-04-30'))

# END EXPERIMENTAL

pass

# Places are any lat/long position, the following are the locations of Oracle's cloud regions
# Only places that have a GA date (valid_from) in the past are considered
# OCI Regions from https://docs.cloud.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
oci_regions = [
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
    place('eu-stockholm-1', 'Stockholm', latlong(59.329444, 18.068611), '2021-12-17'),
    place('eu-milan-1', 'Milan', latlong(45.4636183, 9.1881156), '2021-11-20'),
    place('af-johannesburg-1', 'Johannesburg', latlong(-26.201452, 28.045488), '2022-01-08'),
    place('eu-paris-1', 'Paris', latlong(48.856895, 2.3508487), '2022-02-28'),
    place('eu-madrid-1', 'Madrid', latlong(40.4167, -3.7003), '2022-03-09'),
    place('mx-queretaro-1', 'Queretaro', latlong(20.5875, -100.392778), '2023-01-01')
]

summer_olympics = [
    place('Athens', 'Summer 1896,2004', latlong(37.9839412, 23.7283052), '6/4/1896'),
    place('Paris', 'Summer 1900,1924,2024', latlong(48.8534951, 2.3483915), '1900-05-14'),
    place('St. Louis', 'Summer 1904', latlong(52.9211149, -105.8091459), '1904-07-01'),
    place('London', 'Summer 1908,1948,2012', latlong(51.5073219, -0.1276474), '1908-04-27'),
    place('Stockholm', 'Summer 1912', latlong(59.3251172, 18.0710935), '1912-07-06'),
    place('Antwerp', 'Summer 1920', latlong(51.2211097, 4.3997081), '1920-08-14'),
    place('Amsterdam', 'Summer 1928', latlong(52.3727598, 4.8936041), '1928-07-28'),
    place('Los Angeles', 'Summer 1932,1984,2028', latlong(34.0536909, -118.242766), '1932-07-30'),
    place('Berlin', 'Summer 1936', latlong(52.5170365, 13.3888599), '1936-08-01'),
    place('Helsinki', 'Summer 1952', latlong(60.1674881, 24.9427473), '1952-07-19'),
    place('Melbourne', 'Summer 1956', latlong(-37.8142176, 144.9631608), '1956-11-22'),
    place('Rome', 'Summer 1960', latlong(41.8933203, 12.4829321), '1960-08-25'),
    place('Tokyo', 'Summer 1964,2020', latlong(35.6828387, 139.7594549), '1964-10-10'),
    place('Mexico City', 'Summer 1968', latlong(19.4326296, -99.1331785), '1968-10-12'),
    place('Munich', 'Summer 1972', latlong(48.1371079, 11.5753822), '1972-08-26'),
    place('Montreal', 'Summer 1976', latlong(45.5031824, -73.5698065), '1976-07-17'),
    place('Moscow', 'Summer 1980', latlong(55.7504461, 37.6174943), '1980-07-19'),
    place('Seoul', 'Summer 1988', latlong(37.5666791, 126.9782914), '1988-09-17'),
    place('Barcelona', 'Summer 1992', latlong(41.387917, 2.1699187), '1992-07-25'),
    place('Atlanta', 'Summer 1996', latlong(33.7489924, -84.3902644), '1996-07-19'),
    place('Sydney', 'Summer 2000', latlong(-33.8698439, 151.2082848), '2000-09-15'),
    place('Beijing', 'Summer 2008', latlong(39.906217, 116.3912757), '2008-08-08'),
    place('Rio de Janeiro', 'Summer 2016', latlong(-22.9110137, -43.2093727), '2016-08-05'),
    place('Brisbane', 'Summer 2032', latlong(37.687165, -122.402794), '2032-07-23'),
]

winter_olympics = [
    place('Chamonix', 'Winter 1924', latlong(45.9231, 6.8697), '1924-01-25'),
    place('St. Moritz', 'Winter 1928,1948', latlong(46.4978958, 9.8392428), '1928-02-11'),
    place('Lake Placid', 'Winter 1932,1980', latlong(27.2930999, -81.3628502), '1932-02-04'),
    place('Garmisch-Partenkirchen', 'Winter 1936', latlong(47.4923741, 11.0962815), '1936-02-06'),
    place('Oslo', 'Winter 1952', latlong(59.9133301, 10.7389701), '1952-02-14'),
    place('Cortina d''Ampezzo', 'Winter 1956', latlong(46.5383332, 12.1373506), '1956-01-26'),
    place('Squaw Valley', 'Winter 1960', latlong(36.7402261, -119.246785), '1960-02-18'),
    place('Innsbruck', 'Winter 1964', latlong(47.2654296, 11.3927685), '1964-01-29'),
    place('Grenoble', 'Winter 1968', latlong(45.1875602, 5.7357819), '1968-02-06'),
    place('Sapporo', 'Winter 1972', latlong(43.061936, 141.3542924), '1972-02-03'),
    place('Innsbruck', 'Winter 1976', latlong(47.2654296, 11.3927685), '1976-02-04'),
    place('Sarajevo', 'Winter 1984', latlong(43.8519774, 18.3866868), '1984-02-08'),
    place('Calgary', 'Winter 1988', latlong(51.047306, -114.05797), '1988-02-13'),
    place('Albertville', 'Winter 1992', latlong(45.6754622, 6.3925417), '1992-02-08'),
    place('Lillehammer', 'Winter 1994', latlong(61.1145451, 10.4670073), '1994-02-12'),
    place('Nagano', 'Winter 1998', latlong(36.1143945, 138.0319015), '1998-02-07'),
    place('Salt Lake City', 'Winter 2002', latlong(40.7596198, -111.8867975), '2002-02-08'),
    place('Turin', 'Winter 2006', latlong(45.0677551, 7.6824892), '2006-02-10'),
    place('Vancouver', 'Winter 2010', latlong(49.2608724, -123.113952), '2010-02-12'),
    place('Sochi', 'Winter 2014', latlong(43.5854823, 39.723109), '2014-02-07'),
    place('Pyeongchang', 'Winter 2018', latlong(37.583766, 128.320312), '2018-02-09'),
    place('Beijing', 'Winter 2022', latlong(39.906217, 116.3912757), '2022-02-04'),
    place('Milan–Cortina d''Ampezzo', 'Winter 2026', latlong(45.4641943, 9.1896346), '2026-02-06'),
]

capitals = [
    place('Kabul', 'Afghanistan', latlong(34.51666667, 69.183333), '1900-01-01'),
    place('Mariehamn', 'Aland Islands', latlong(60.116667, 19.9), '1900-01-01'),
    place('Tirana', 'Albania', latlong(41.31666667, 19.816667), '1900-01-01'),
    place('Algiers', 'Algeria', latlong(36.75, 3.05), '1900-01-01'),
    place('Pago Pago', 'American Samoa', latlong(-14.26666667, -170.7), '1900-01-01'),
    place('Andorra la Vella', 'Andorra', latlong(42.5, 1.516667), '1900-01-01'),
    place('Luanda', 'Angola', latlong(-8.833333333, 13.216667), '1900-01-01'),
    place('The Valley', 'Anguilla', latlong(18.21666667, -63.05), '1900-01-01'),
    place('South Pole', 'Antarctica', latlong(-90, 0), '1900-01-01'),
    place('Saint John''s', 'Antigua and Barbuda', latlong(17.11666667, -61.85), '1900-01-01'),
    place('Buenos Aires', 'Argentina', latlong(-34.58333333, -58.666667), '1900-01-01'),
    place('Yerevan', 'Armenia', latlong(40.16666667, 44.5), '1900-01-01'),
    place('Oranjestad', 'Aruba', latlong(12.51666667, -70.033333), '1900-01-01'),
    place('Canberra', 'Australia', latlong(-35.26666667, 149.133333), '1900-01-01'),
    place('Vienna', 'Austria', latlong(48.2, 16.366667), '1900-01-01'),
    place('Baku', 'Azerbaijan', latlong(40.38333333, 49.866667), '1900-01-01'),
    place('Nassau', 'Bahamas', latlong(25.08333333, -77.35), '1900-01-01'),
    place('Manama', 'Bahrain', latlong(26.23333333, 50.566667), '1900-01-01'),
    place('Dhaka', 'Bangladesh', latlong(23.71666667, 90.4), '1900-01-01'),
    place('Bridgetown', 'Barbados', latlong(13.1, -59.616667), '1900-01-01'),
    place('Minsk', 'Belarus', latlong(53.9, 27.566667), '1900-01-01'),
    place('Brussels', 'Belgium', latlong(50.83333333, 4.333333), '1900-01-01'),
    place('Belmopan', 'Belize', latlong(17.25, -88.766667), '1900-01-01'),
    place('Porto-Novo', 'Benin', latlong(6.483333333, 2.616667), '1900-01-01'),
    place('Hamilton', 'Bermuda', latlong(32.28333333, -64.783333), '1900-01-01'),
    place('Thimphu', 'Bhutan', latlong(27.46666667, 89.633333), '1900-01-01'),
    place('La Paz', 'Bolivia', latlong(-16.5, -68.15), '1900-01-01'),
    place('Sarajevo', 'Bosnia and Herzegovina', latlong(43.86666667, 18.416667), '1900-01-01'),
    place('Gaborone', 'Botswana', latlong(-24.63333333, 25.9), '1900-01-01'),
    place('Brasilia', 'Brazil', latlong(-15.78333333, -47.916667), '1900-01-01'),
    place('Diego Garcia', 'British Indian Ocean Territory', latlong(-7.3, 72.4), '1900-01-01'),
    place('Road Town', 'British Virgin Islands', latlong(18.41666667, -64.616667), '1900-01-01'),
    place('Bandar Seri Begawan', 'Brunei Darussalam', latlong(4.883333333, 114.933333), '1900-01-01'),
    place('Sofia', 'Bulgaria', latlong(42.68333333, 23.316667), '1900-01-01'),
    place('Ouagadougou', 'Burkina Faso', latlong(12.36666667, -1.516667), '1900-01-01'),
    place('Bujumbura', 'Burundi', latlong(-3.366666667, 29.35), '1900-01-01'),
    place('Phnom Penh', 'Cambodia', latlong(11.55, 104.916667), '1900-01-01'),
    place('Yaounde', 'Cameroon', latlong(3.866666667, 11.516667), '1900-01-01'),
    place('Ottawa', 'Canada', latlong(45.41666667, -75.7), '1900-01-01'),
    place('Praia', 'Cape Verde', latlong(14.91666667, -23.516667), '1900-01-01'),
    place('George Town', 'Cayman Islands', latlong(19.3, -81.383333), '1900-01-01'),
    place('Bangui', 'Central African Republic', latlong(4.366666667, 18.583333), '1900-01-01'),
    place('N''Djamena', 'Chad', latlong(12.1, 15.033333), '1900-01-01'),
    place('Santiago', 'Chile', latlong(-33.45, -70.666667), '1900-01-01'),
    place('Beijing', 'China', latlong(39.91666667, 116.383333), '1900-01-01'),
    place('The Settlement', 'Christmas Island', latlong(-10.41666667, 105.716667), '1900-01-01'),
    place('West Island', 'Cocos Islands', latlong(-12.16666667, 96.833333), '1900-01-01'),
    place('Bogota', 'Colombia', latlong(4.6, -74.083333), '1900-01-01'),
    place('Moroni', 'Comoros', latlong(-11.7, 43.233333), '1900-01-01'),
    place('Avarua', 'Cook Islands', latlong(-21.2, -159.766667), '1900-01-01'),
    place('San Jose', 'Costa Rica', latlong(9.933333333, -84.083333), '1900-01-01'),
    place('Yamoussoukro', 'Cote d’Ivoire', latlong(6.816666667, -5.266667), '1900-01-01'),
    place('Zagreb', 'Croatia', latlong(45.8, 16), '1900-01-01'),
    place('Havana', 'Cuba', latlong(23.11666667, -82.35), '1900-01-01'),
    place('Willemstad', 'Curaçao', latlong(12.1, -68.916667), '1900-01-01'),
    place('Nicosia', 'Cyprus', latlong(35.16666667, 33.366667), '1900-01-01'),
    place('Prague', 'Czech Republic', latlong(50.08333333, 14.466667), '1900-01-01'),
    place('Kinshasa', 'Democratic Republic of the Congo', latlong(-4.316666667, 15.3), '1900-01-01'),
    place('Copenhagen', 'Denmark', latlong(55.66666667, 12.583333), '1900-01-01'),
    place('Djibouti', 'Djibouti', latlong(11.58333333, 43.15), '1900-01-01'),
    place('Roseau', 'Dominica', latlong(15.3, -61.4), '1900-01-01'),
    place('Santo Domingo', 'Dominican Republic', latlong(18.46666667, -69.9), '1900-01-01'),
    place('Quito', 'Ecuador', latlong(-0.216666667, -78.5), '1900-01-01'),
    place('Cairo', 'Egypt', latlong(30.05, 31.25), '1900-01-01'),
    place('San Salvador', 'El Salvador', latlong(13.7, -89.2), '1900-01-01'),
    place('Malabo', 'Equatorial Guinea', latlong(3.75, 8.783333), '1900-01-01'),
    place('Asmara', 'Eritrea', latlong(15.33333333, 38.933333), '1900-01-01'),
    place('Tallinn', 'Estonia', latlong(59.43333333, 24.716667), '1900-01-01'),
    place('Addis Ababa', 'Ethiopia', latlong(9.033333333, 38.7), '1900-01-01'),
    place('Stanley', 'Falkland Islands', latlong(-51.7, -57.85), '1900-01-01'),
    place('Torshavn', 'Faroe Islands', latlong(62, -6.766667), '1900-01-01'),
    place('Palikir', 'Federated States of Micronesia', latlong(6.916666667, 158.15), '1900-01-01'),
    place('Suva', 'Fiji', latlong(-18.13333333, 178.416667), '1900-01-01'),
    place('Helsinki', 'Finland', latlong(60.16666667, 24.933333), '1900-01-01'),
    place('Paris', 'France', latlong(48.86666667, 2.333333), '1900-01-01'),
    place('Papeete', 'French Polynesia', latlong(-17.53333333, -149.566667), '1900-01-01'),
    # place('Port-aux-Français', 'French Southern and Antarctic Lands', latlong(-49.35, 70.216667), '1900-01-01'),
    place('Libreville', 'Gabon', latlong(0.383333333, 9.45), '1900-01-01'),
    place('Tbilisi', 'Georgia', latlong(41.68333333, 44.833333), '1900-01-01'),
    place('Berlin', 'Germany', latlong(52.51666667, 13.4), '1900-01-01'),
    place('Accra', 'Ghana', latlong(5.55, -0.216667), '1900-01-01'),
    place('Gibraltar', 'Gibraltar', latlong(36.13333333, -5.35), '1900-01-01'),
    place('Athens', 'Greece', latlong(37.98333333, 23.733333), '1900-01-01'),
    place('Nuuk', 'Greenland', latlong(64.18333333, -51.75), '1900-01-01'),
    place('Saint George''s', 'Grenada', latlong(12.05, -61.75), '1900-01-01'),
    place('Hagatna', 'Guam', latlong(13.46666667, 144.733333), '1900-01-01'),
    place('Guatemala City', 'Guatemala', latlong(14.61666667, -90.516667), '1900-01-01'),
    place('Saint Peter Port', 'Guernsey', latlong(49.45, -2.533333), '1900-01-01'),
    place('Conakry', 'Guinea', latlong(9.5, -13.7), '1900-01-01'),
    place('Bissau', 'Guinea-Bissau', latlong(11.85, -15.583333), '1900-01-01'),
    place('Georgetown', 'Guyana', latlong(6.8, -58.15), '1900-01-01'),
    place('Port-au-Prince', 'Haiti', latlong(18.53333333, -72.333333), '1900-01-01'),
    place('Tegucigalpa', 'Honduras', latlong(14.1, -87.216667), '1900-01-01'),
    place('Hong Kong', 'Hong Kong', latlong(22.3, 114.2), '1900-01-01'),
    place('Budapest', 'Hungary', latlong(47.5, 19.083333), '1900-01-01'),
    place('Reykjavik', 'Iceland', latlong(64.15, -21.95), '1900-01-01'),
    place('New Delhi', 'India', latlong(28.6, 77.2), '1900-01-01'),
    place('Jakarta', 'Indonesia', latlong(-6.166666667, 106.816667), '1900-01-01'),
    place('Tehran', 'Iran', latlong(35.7, 51.416667), '1900-01-01'),
    place('Baghdad', 'Iraq', latlong(33.33333333, 44.4), '1900-01-01'),
    place('Dublin', 'Ireland', latlong(53.31666667, -6.233333), '1900-01-01'),
    place('Douglas', 'Isle of Man', latlong(54.15, -4.483333), '1900-01-01'),
    place('Jerusalem', 'Israel', latlong(31.76666667, 35.233333), '1900-01-01'),
    place('Rome', 'Italy', latlong(41.9, 12.483333), '1900-01-01'),
    place('Kingston', 'Jamaica', latlong(18, -76.8), '1900-01-01'),
    place('Tokyo', 'Japan', latlong(35.68333333, 139.75), '1900-01-01'),
    place('Saint Helier', 'Jersey', latlong(49.18333333, -2.1), '1900-01-01'),
    place('Amman', 'Jordan', latlong(31.95, 35.933333), '1900-01-01'),
    place('Astana', 'Kazakhstan', latlong(51.16666667, 71.416667), '1900-01-01'),
    place('Nairobi', 'Kenya', latlong(-1.283333333, 36.816667), '1900-01-01'),
    place('Tarawa', 'Kiribati', latlong(-0.883333333, 169.533333), '1900-01-01'),
    place('Pristina', 'Kosovo', latlong(42.66666667, 21.166667), '1900-01-01'),
    place('Kuwait City', 'Kuwait', latlong(29.36666667, 47.966667), '1900-01-01'),
    place('Bishkek', 'Kyrgyzstan', latlong(42.86666667, 74.6), '1900-01-01'),
    place('Vientiane', 'Laos', latlong(17.96666667, 102.6), '1900-01-01'),
    place('Riga', 'Latvia', latlong(56.95, 24.1), '1900-01-01'),
    place('Beirut', 'Lebanon', latlong(33.86666667, 35.5), '1900-01-01'),
    place('Maseru', 'Lesotho', latlong(-29.31666667, 27.483333), '1900-01-01'),
    place('Monrovia', 'Liberia', latlong(6.3, -10.8), '1900-01-01'),
    place('Tripoli', 'Libya', latlong(32.88333333, 13.166667), '1900-01-01'),
    place('Vaduz', 'Liechtenstein', latlong(47.13333333, 9.516667), '1900-01-01'),
    place('Vilnius', 'Lithuania', latlong(54.68333333, 25.316667), '1900-01-01'),
    place('Luxembourg', 'Luxembourg', latlong(49.6, 6.116667), '1900-01-01'),
    place('Macau', 'Macau', latlong(22.166667, 113.55), '1900-01-01'),
    place('Skopje', 'Macedonia', latlong(42, 21.433333), '1900-01-01'),
    place('Antananarivo', 'Madagascar', latlong(-18.91666667, 47.516667), '1900-01-01'),
    place('Lilongwe', 'Malawi', latlong(-13.96666667, 33.783333), '1900-01-01'),
    place('Kuala Lumpur', 'Malaysia', latlong(3.166666667, 101.7), '1900-01-01'),
    place('Male', 'Maldives', latlong(4.166666667, 73.5), '1900-01-01'),
    place('Bamako', 'Mali', latlong(12.65, -8), '1900-01-01'),
    place('Valletta', 'Malta', latlong(35.88333333, 14.5), '1900-01-01'),
    place('Majuro', 'Marshall Islands', latlong(7.1, 171.383333), '1900-01-01'),
    place('Nouakchott', 'Mauritania', latlong(18.06666667, -15.966667), '1900-01-01'),
    place('Port Louis', 'Mauritius', latlong(-20.15, 57.483333), '1900-01-01'),
    place('Mexico City', 'Mexico', latlong(19.43333333, -99.133333), '1900-01-01'),
    place('Chisinau', 'Moldova', latlong(47, 28.85), '1900-01-01'),
    place('Monaco', 'Monaco', latlong(43.73333333, 7.416667), '1900-01-01'),
    place('Ulaanbaatar', 'Mongolia', latlong(47.91666667, 106.916667), '1900-01-01'),
    place('Podgorica', 'Montenegro', latlong(42.43333333, 19.266667), '1900-01-01'),
    place('Plymouth', 'Montserrat', latlong(16.7, -62.216667), '1900-01-01'),
    place('Rabat', 'Morocco', latlong(34.01666667, -6.816667), '1900-01-01'),
    place('Maputo', 'Mozambique', latlong(-25.95, 32.583333), '1900-01-01'),
    place('Rangoon', 'Myanmar', latlong(16.8, 96.15), '1900-01-01'),
    place('Windhoek', 'Namibia', latlong(-22.56666667, 17.083333), '1900-01-01'),
    place('Yaren', 'Nauru', latlong(-0.5477, 166.920867), '1900-01-01'),
    place('Kathmandu', 'Nepal', latlong(27.71666667, 85.316667), '1900-01-01'),
    place('Amsterdam', 'Netherlands', latlong(52.35, 4.916667), '1900-01-01'),
    place('Noumea', 'New Caledonia', latlong(-22.26666667, 166.45), '1900-01-01'),
    place('Wellington', 'New Zealand', latlong(-41.3, 174.783333), '1900-01-01'),
    place('Managua', 'Nicaragua', latlong(12.13333333, -86.25), '1900-01-01'),
    place('Niamey', 'Niger', latlong(13.51666667, 2.116667), '1900-01-01'),
    place('Abuja', 'Nigeria', latlong(9.083333333, 7.533333), '1900-01-01'),
    place('Alofi', 'Niue', latlong(-19.01666667, -169.916667), '1900-01-01'),
    place('Kingston', 'Norfolk Island', latlong(-29.05, 167.966667), '1900-01-01'),
    place('Pyongyang', 'North Korea', latlong(39.01666667, 125.75), '1900-01-01'),
    place('North Nicosia', 'Northern Cyprus', latlong(35.183333, 33.366667), '1900-01-01'),
    place('Saipan', 'Northern Mariana Islands', latlong(15.2, 145.75), '1900-01-01'),
    place('Oslo', 'Norway', latlong(59.91666667, 10.75), '1900-01-01'),
    place('Muscat', 'Oman', latlong(23.61666667, 58.583333), '1900-01-01'),
    place('Islamabad', 'Pakistan', latlong(33.68333333, 73.05), '1900-01-01'),
    place('Melekeok', 'Palau', latlong(7.483333333, 134.633333), '1900-01-01'),
    place('Jerusalem', 'Palestine', latlong(31.76666667, 35.233333), '1900-01-01'),
    place('Panama City', 'Panama', latlong(8.966666667, -79.533333), '1900-01-01'),
    place('Port Moresby', 'Papua New Guinea', latlong(-9.45, 147.183333), '1900-01-01'),
    place('Asuncion', 'Paraguay', latlong(-25.26666667, -57.666667), '1900-01-01'),
    place('Lima', 'Peru', latlong(-12.05, -77.05), '1900-01-01'),
    place('Manila', 'Philippines', latlong(14.6, 120.966667), '1900-01-01'),
    place('Adamstown', 'Pitcairn Islands', latlong(-25.06666667, -130.083333), '1900-01-01'),
    place('Warsaw', 'Poland', latlong(52.25, 21), '1900-01-01'),
    place('Lisbon', 'Portugal', latlong(38.71666667, -9.133333), '1900-01-01'),
    place('San Juan', 'Puerto Rico', latlong(18.46666667, -66.116667), '1900-01-01'),
    place('Doha', 'Qatar', latlong(25.28333333, 51.533333), '1900-01-01'),
    place('Brazzaville', 'Republic of Congo', latlong(-4.25, 15.283333), '1900-01-01'),
    place('Bucharest', 'Romania', latlong(44.43333333, 26.1), '1900-01-01'),
    place('Moscow', 'Russia', latlong(55.75, 37.6), '1900-01-01'),
    place('Kigali', 'Rwanda', latlong(-1.95, 30.05), '1900-01-01'),
    place('Gustavia', 'Saint Barthelemy', latlong(17.88333333, -62.85), '1900-01-01'),
    place('Jamestown', 'Saint Helena', latlong(-15.93333333, -5.716667), '1900-01-01'),
    place('Basseterre', 'Saint Kitts and Nevis', latlong(17.3, -62.716667), '1900-01-01'),
    place('Castries', 'Saint Lucia', latlong(14, -61), '1900-01-01'),
    place('Marigot', 'Saint Martin', latlong(18.0731, -63.0822), '1900-01-01'),
    place('Saint-Pierre', 'Saint Pierre and Miquelon', latlong(46.76666667, -56.183333), '1900-01-01'),
    place('Kingstown', 'Saint Vincent and the Grenadines', latlong(13.13333333, -61.216667), '1900-01-01'),
    place('Apia', 'Samoa', latlong(-13.81666667, -171.766667), '1900-01-01'),
    place('San Marino', 'San Marino', latlong(43.93333333, 12.416667), '1900-01-01'),
    place('Sao Tome', 'Sao Tome and Principe', latlong(0.333333333, 6.733333), '1900-01-01'),
    place('Riyadh', 'Saudi Arabia', latlong(24.65, 46.7), '1900-01-01'),
    place('Dakar', 'Senegal', latlong(14.73333333, -17.633333), '1900-01-01'),
    place('Belgrade', 'Serbia', latlong(44.83333333, 20.5), '1900-01-01'),
    place('Victoria', 'Seychelles', latlong(-4.616666667, 55.45), '1900-01-01'),
    place('Freetown', 'Sierra Leone', latlong(8.483333333, -13.233333), '1900-01-01'),
    place('Singapore', 'Singapore', latlong(1.283333333, 103.85), '1900-01-01'),
    place('Philipsburg', 'Sint Maarten', latlong(18.01666667, -63.033333), '1900-01-01'),
    place('Bratislava', 'Slovakia', latlong(48.15, 17.116667), '1900-01-01'),
    place('Ljubljana', 'Slovenia', latlong(46.05, 14.516667), '1900-01-01'),
    place('Honiara', 'Solomon Islands', latlong(-9.433333333, 159.95), '1900-01-01'),
    place('Mogadishu', 'Somalia', latlong(2.066666667, 45.333333), '1900-01-01'),
    place('Hargeisa', 'Somaliland', latlong(9.55, 44.05), '1900-01-01'),
    place('Pretoria', 'South Africa', latlong(-25.7, 28.216667), '1900-01-01'),
    place('King Edward Point', 'South Georgia and South Sandwich Islands', latlong(-54.283333, -36.5), '1900-01-01'),
    place('Seoul', 'South Korea', latlong(37.55, 126.983333), '1900-01-01'),
    place('Juba', 'South Sudan', latlong(4.85, 31.616667), '1900-01-01'),
    place('Madrid', 'Spain', latlong(40.4, -3.683333), '1900-01-01'),
    place('Colombo', 'Sri Lanka', latlong(6.916666667, 79.833333), '1900-01-01'),
    place('Khartoum', 'Sudan', latlong(15.6, 32.533333), '1900-01-01'),
    place('Paramaribo', 'Suriname', latlong(5.833333333, -55.166667), '1900-01-01'),
    place('Longyearbyen', 'Svalbard', latlong(78.21666667, 15.633333), '1900-01-01'),
    place('Mbabane', 'Swaziland', latlong(-26.31666667, 31.133333), '1900-01-01'),
    place('Stockholm', 'Sweden', latlong(59.33333333, 18.05), '1900-01-01'),
    place('Bern', 'Switzerland', latlong(46.91666667, 7.466667), '1900-01-01'),
    place('Damascus', 'Syria', latlong(33.5, 36.3), '1900-01-01'),
    place('Taipei', 'Taiwan', latlong(25.03333333, 121.516667), '1900-01-01'),
    place('Dushanbe', 'Tajikistan', latlong(38.55, 68.766667), '1900-01-01'),
    place('Dar es Salaam', 'Tanzania', latlong(-6.8, 39.283333), '1900-01-01'),
    place('Bangkok', 'Thailand', latlong(13.75, 100.516667), '1900-01-01'),
    place('Banjul', 'The Gambia', latlong(13.45, -16.566667), '1900-01-01'),
    place('Dili', 'Timor-Leste', latlong(-8.583333333, 125.6), '1900-01-01'),
    place('Lome', 'Togo', latlong(6.116666667, 1.216667), '1900-01-01'),
    place('Atafu', 'Tokelau', latlong(-9.166667, -171.833333), '1900-01-01'),
    place('Nuku''alofa', 'Tonga', latlong(-21.13333333, -175.2), '1900-01-01'),
    place('Port of Spain', 'Trinidad and Tobago', latlong(10.65, -61.516667), '1900-01-01'),
    place('Tunis', 'Tunisia', latlong(36.8, 10.183333), '1900-01-01'),
    place('Ankara', 'Turkey', latlong(39.93333333, 32.866667), '1900-01-01'),
    place('Ashgabat', 'Turkmenistan', latlong(37.95, 58.383333), '1900-01-01'),
    place('Grand Turk', 'Turks and Caicos Islands', latlong(21.46666667, -71.133333), '1900-01-01'),
    place('Funafuti', 'Tuvalu', latlong(-8.516666667, 179.216667), '1900-01-01'),
    place('Kampala', 'Uganda', latlong(0.316666667, 32.55), '1900-01-01'),
    place('Kyiv', 'Ukraine', latlong(50.43333333, 30.516667), '1900-01-01'),
    place('Abu Dhabi', 'United Arab Emirates', latlong(24.46666667, 54.366667), '1900-01-01'),
    place('London', 'United Kingdom', latlong(51.5, -0.083333), '1900-01-01'),
    place('Washington, D.C.', 'United States', latlong(38.883333, -77), '1900-01-01'),
    place('Montevideo', 'Uruguay', latlong(-34.85, -56.166667), '1900-01-01'),
    place('Charlotte Amalie', 'US Virgin Islands', latlong(18.35, -64.933333), '1900-01-01'),
    place('Tashkent', 'Uzbekistan', latlong(41.31666667, 69.25), '1900-01-01'),
    place('Port-Vila', 'Vanuatu', latlong(-17.73333333, 168.316667), '1900-01-01'),
    place('Vatican City', 'Vatican City', latlong(41.9, 12.45), '1900-01-01'),
    place('Caracas', 'Venezuela', latlong(10.48333333, -66.866667), '1900-01-01'),
    place('Hanoi', 'Vietnam', latlong(21.03333333, 105.85), '1900-01-01'),
    place('Mata-Utu', 'Wallis and Futuna', latlong(-13.95, -171.933333), '1900-01-01'),
    place('El-Aaiun', 'Western Sahara', latlong(27.153611, -13.203333), '1900-01-01'),
    place('Sanaa', 'Yemen', latlong(15.35, 44.2), '1900-01-01'),
    place('Lusaka', 'Zambia', latlong(-15.41666667, 28.283333), '1900-01-01'),
    place('Harare', 'Zimbabwe', latlong(-17.81666667, 31.033333), '1900-01-01'),
]
test_places = [
    place('London', 'Summer 1908,1948,2012', latlong(51.5073219, -0.1276474), '1908-04-27'),
    place('zero-zero', 'Nowhere', latlong(0, 0), '1900-01-01'),
]

# EXPERIMENTAL: Read places from a CSV file
# ====================================================================================================================
# ====================================================================================================================
# CSV Format:
# Country,Valid from Date,Capital Name,Lat,Long
PLACES_FILE = 'capitals.csv'
# PLACES_FILE = 'grid.csv'

csvplaces = []
got_first = False

with open(PLACES_FILE, 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    next(csv_reader, None)  # skip the header
    for line in csv_reader:
        if len(line) != 0:
            # City, Co
            # untry, Lat, Long, Date
            # print(f"{line}, {len(line)} ")
            csvplaces.append(place(line[2], line[0], latlong(float(line[3]), float(line[4])), line[1]))
# ====================================================================================================================
# ====================================================================================================================

# places = oci_regions
# places = summer_olympics + winter_olympics
places = capitals
# places = test_places
# places = csvplaces

R = 6378.1  # Radius of Earth (km)


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
    # Only check places with valid_from before the given date or today
    # Optional: on-date
    if on_date == '':
        on_date = date.today().strftime("%Y-%d-%d")
    closest_dist_km = 99999
    closest_place = 'NOTFOUND'

    for r in [p for p in places if p.valid_from < on_date]:
        d = dist_between(r.latlong, location)

        if d < closest_dist_km:
            closest_dist_km = d
            closest_place = r

    return closest_place, closest_dist_km


# Main for testing only
if __name__ == '__main__':
    t_city, t_dist = closest_place_to(latlong(55, 0))
    print(f"Closest place is {t_city} ({t_dist:.0f} km)")
