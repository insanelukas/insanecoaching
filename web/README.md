# Site-side tools for the quiz media (copies; the working files live with the site sources, which are not in this repository)

- `set_media.py MODE` writes the `var MEDIA = {...};` line of the page source. `hybrid` (in use): files of the site wherever they exist for the
  clip in use: small clips (`vid/g/<key>.mp4`, `vid/s/<key>.mp4`, made by the media workflow into `out/vid`) and stills
  (`img/g/<key>.jpg`, `img/s/<key>.jpg`, each the first frame of its clip); the Higgsfield result address is only the fallback.
- `tiles.py` cuts those stills out of the sheets made by `media/frames.py` with `jpegtran -crop` (no second encoding) and keeps `stills.json`.
- `stills.json`: which clip (job id) each still was taken from, as of the deploy `d856b73` on main (2026-11-24): 30 loops, 150 scenes. `out/done.json` says the same for the small clips.
- `ownmedia.js`: test helper; answers requests for the site's own stills from local files.

The stills and the small clips themselves are in the site (branch `main`: `img/g`, `img/s`, `vid/g`, `vid/s`).
