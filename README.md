EDMC-Astrodraw
==============

## Plan

- [ ] Map
  - [ ] Get necessary tiles
    - URL format: https://edastro.b-cdn.net/galmap/tiles/indexedheat/?/?/?.png
    - Find out the tile-coordinate mapping
  - [ ] Get timestamp of current heatmap
    - `timestamp_tiles` variable from https://edastro.com/galmap/galmap.js
  - [ ] Get from journal only the systems discovered afterwards
  - [ ] Get colors of target pixels and recalculate with the added systems
    - https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.LinearSegmentedColormap.html
    - Compute and store reverse map for entire 0-5000 range
- [ ] Button bar
  - [ ] Load file
    - One `x, z` point per line
    - Separator for disjointed elements
  - [ ] Load journal(s)
  - [ ] Toggle drawing
  - [ ] Toggle predicted