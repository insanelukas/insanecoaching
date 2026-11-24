# Site-side tools for the quiz media (copies; the working files live with the site sources, which are not in this repository)

- `set_media.py MODE` writes the `var MEDIA = {...};` line of the page source. `hybrid` (in use): clips at the Higgsfield result addresses,
  stills as files of the site (`img/g/<key>.jpg`, `img/s/<key>.jpg`), each the first frame of its clip.
- `tiles.py` cuts those stills out of the sheets made by `media/frames.py` with `jpegtran -crop` (no second encoding) and keeps `stills.json`.
- `stills.json`: which clip (job id) each still was taken from, as of the deploy `c2be8a1` on main (2026-11-24): 30 loops, 150 scenes.
- `ownmedia.js`: test helper; answers requests for the site's own stills from local files.

The stills themselves are in the site (branch `main`, `img/g` and `img/s`).
