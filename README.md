EDMC-Astrodraw
==============

## Development plan

- [x] Timestamp of latest update
    - The map's timestamp is rendered directly in it, and thus cannot be trivially parsed
    - The tile generation timestamp, however, is part of the client code
    - Parse `var timestamp_tiles...` line from https://edastro.com/galmap/galmap.js
- [ ] Map
  - [x] Get relevant tiles
    - URL format: `https://edastro.b-cdn.net/galmap/tiles/indexedheat/{zoom}/{x}/{y}.png`
    - Zoom level 6 is the original size, 1px = 10ly
    - ED to map coordinates:
      - `Xm = Xe/10 + 8192`
      - `Ym = (Ze-25000)/10 - 8192`
    - Each tile is 256x256
  - [x] Show player position
  - [ ] Show player route
  - [ ] Get system discoveries dated after latest update
    - The gap between generating the map and tiles means that any estimations are pessimistic
  - [x] Update colors of affected points
- [ ] Button bar
  - [x] Load file
    - One `x, z` point per line
  - [ ] Load external journal(s)
  - [x] Toggle drawing
  - [x] Toggle estimate