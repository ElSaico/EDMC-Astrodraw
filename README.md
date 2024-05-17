EDMC-Astrodraw
==============

## Development plan

- [ ] Timestamp of latest update
    - The map's timestamp is rendered directly in it, and thus cannot be trivially parsed
    - The tiles, however, take a while to generate - and its timestamp is used by client code
    - Parse `var timestamp_tiles...` line from https://edastro.com/galmap/galmap.js
- [ ] Map
  - [ ] Get relevant tiles
    - URL format: `https://edastro.b-cdn.net/galmap/tiles/indexedheat/{zoom}/{x}/{y}.png`
    - Zoom level 6 is the original size, 1px = 10ly
    - ED to map coordinates:
      - `Xm = Xe/10 + 8192`
      - `Ym = (Ze-25000)/10 - 8192`
    - Each tile is 256x256
  - [ ] Get system discoveries dated after latest update
    - The gap between generating the map and tiles means that any predictions are pessimistic
  - [ ] Update colors of affected points
- [ ] Button bar
  - [ ] Load file
    - One `x, z` point per line
    - Separator for disjointed elements
  - [ ] Load external journal(s)
  - [ ] Toggle drawing
  - [ ] Toggle predicted