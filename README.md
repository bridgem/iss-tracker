## ISS Tracker
![Animation](animation.gif)

Inspired by the NASA ISS Tracker: https://spotthestation.nasa.gov/tracking_map.cfm

This version adds a list of places and shows which one is currently the closest to the ISS.
Originally built as a novel way to highlight Oracle OCI cloud regions round the world.

It uses satellite data from NORAD and the skyfield python library to compute the satellite's position. It launches a separate window using pygame.
Each ISS orbits is roughly 90 minutes, but you can control the speed to go into th future or the past!

Two main scripts:
* iss_tracker.py - a simple text based output showing ISS data and closest place
* iss_tracker_pygame - a graphical version showing all the locations from a supplied list and the orbit of the ISS

The pygame app responds to the following keys:
```
    +/-      Speed up/slow down the ISS
    1        Reset ISS speed to real time
    P        Pause (freeze movement)
    R        Reset to current (actual) ISS position
    Esc/Q    Quit
```

Uses fonts Courier New & Calibri; you may need to install them on your system
