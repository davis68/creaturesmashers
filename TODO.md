TODO:

- set up map
    - camera/view updates independently of motion and map
    - multiple layers?
        background, basement, foreground, character, upper
        mask for each, including passability (-1), actions (+2.xx), and chance of random encounter (0.0-1.0)

    - switch to four-element square mask for each (as hex code)
    - combine/transition tiles on map or automatically on load?
- set up menus
    - make them load from config files or string tables
- set up combat
- set up sprites
    - oversized/multi-tile sprites?
    - tileset per map
    - starting coords for PC per map
- set up CSEffect class
- set up CSDialogue class
- set up CSBehaviorPattern class
- profile to optimize


https://realpython.com/blog/python/pygame-a-primer/

320,96
384,384

224,480
480,256
