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
    - 1:1 on zoom 6, 2:1 on 7, 4:1 on 8
    - Find out which tiles correspond to the map coordinates
    - Map to ED coordinates:
      - `x = (1+x/81920)*128`
      - `z = -(1+(25000-y)/81920)*128`
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