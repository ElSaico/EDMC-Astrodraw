EDMC-Astrodraw
==============

## Development plan

- [ ] Map
  - [ ] Get relevant tiles
    - URL format: `https://edastro.b-cdn.net/galmap/tiles/indexedheat/{zoom}/{x}/{y}.png`
    - 1:1 on zoom 6, 2:1 on 7, 4:1 on 8
    - Find out which tiles correspond to the map coordinates
    - Map to ED coordinates:
      - `x = (1+x/81920)*128`
      - `z = -(1+(25000-y)/81920)*128`
  - [ ] Get timestamp of current heatmap
    - `timestamp_tiles` variable from https://edastro.com/galmap/galmap.js
  - [ ] Get from journal only the systems discovered afterwards
  - [ ] Get colors of related pixels, map to values and recalculate with the new systems
- [ ] Button bar
  - [ ] Load file
    - One `x, z` point per line
    - Separator for disjointed elements
  - [ ] Load external journal(s)
  - [ ] Toggle drawing
  - [ ] Toggle predicted