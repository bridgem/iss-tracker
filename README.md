## ISS Tracker

![Animation](animation.gif)

Inspired by the NASA ISS Tracker: https://spotthestation.nasa.gov/tracking_map.cfm

This version adds a list of places and shows which one is currently the closest to the ISS.
Originally built as a novel way to highlight Oracle OCI cloud regions round the world, but can display any list such as capital cities

It uses satellite data from NORAD and the skyfield python library to compute the satellite's position. It launches a separate window using pygame.
Each ISS orbit is roughly 90 minutes, but you can control the speed to go into the future or the past.

Two main scripts:
* iss_tracker.py - a simple text based output showing ISS data and closest place
* iss_tracker_pygame - a graphical version showing all the locations from a supplied list and the orbit of the ISS

The pygame app responds to the following keys:
```
    +/-      Speed up/slow down the ISS
    1        Reset ISS speed to real time
    P        Pause (freeze movement)
    R        Reset to current (actual) ISS position
    N        Display Night/Day terminator
    Esc/Q    Quit
```

Uses fonts Courier New & Calibri. You may need to install them on your system

Images
https://en.wikipedia.org/wiki/Equirectangular_projection#/media/File:Blue_Marble_2002.png
