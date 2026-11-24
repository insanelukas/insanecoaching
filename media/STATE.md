# Media work branch: how it runs (written 2026-11-24)

Goal: 30 game-style quiz characters (still + 5 s loop) and 150 end scenes (still + 5 s clip) for insanecoaching.com,
made on Higgsfield with the free unlimited generations (they end 2026-11-25 10:06 Vilnius time).

- `media/gen.py`: prompts and the job queue. Indexes: 1000+ character still, 2000+ scene still, 3000+ character loop, 4000+ scene clip.
- `media/ids.txt`: the event log (see `gen.load`): `IDX JOB`, `S IDX STAMP`, `A IDX-IDX`, `IDX -`.
- `media/qa.py`: contact sheets (run in the Higgsfield sandbox, which can read the result addresses).
- One cycle: jobs_wait -> append `S` lines here (and new job lines) -> commit, push -> in the sandbox `git checkout media/ids.txt; git pull; python3 media/gen.py next N; python3 media/qa.py LIST ...`
  -> look at the sheet -> approve stills with an `A` line or drop a bad job with `IDX -` -> submit `media/plan/next_vid.json` / `next_img.json` (max 8 jobs run at once).
- Rules learned: a still that the video model refuses ("copyright restrictions" = looks like a known person) is made again with a plainer face;
  a loop whose last frame does not match the first is made again.
- `preview/`: the current site build for a visual check in the sandbox (overlaid on a clone of main). `media/site/shot16.js` walks the quiz and takes screenshots.
- The site reads `MEDIA` (key -> [clip, still]) written by `web/set_media.py` from this log. Mode `cdn` = Higgsfield result addresses; mode `local` = files in the site.

## Status and routine (updated 2026-11-24 15:45 Vilnius time)

- Done and live (main `d856b73`): 30 character loops and 150 end scenes (25 per group: mb, ma, wb, mc, wa, wc), every still and clip looked at on
  contact sheets, every first frame looked at large on the sheets. All test suites pass on that build.
- Found on the way: the video model re-renders the scene, so a clip does NOT open on the still it was made from (`media/match.py` measures it;
  all 156 clips measured differed, many open on a tighter framing). The page shows a still under each clip, so the site now uses each clip's own
  first frame as its still: `media/frames.py` packs the first frames into sheets (one column, at most 500 kB), a sandbox call returns a sheet as a
  picture, `web/tiles.py` cuts the tiles out with `jpegtran -crop` (no second encoding) into `web/media-out/img/g|s/<key>.jpg` and notes in
  `media-out/stills.json` which clip each still belongs to.
- Site media list: `python3 -I set_media.py hybrid` = files of the site wherever `web/media-out` has them for the clip in use (stills `img/g`, `img/s`
  with `stills.json`; small clips `vid/g`, `vid/s` with `clips.json` = a copy of `out/done.json`), the Higgsfield result address otherwise.
  Since `d856b73` every still and every clip is a file of the site and the page asks the service for nothing.
  A clip made again needs: (1) the workflow again for the small clip (change `ci/media.run`, push, wait, pull, copy `out/vid` and `out/done.json`),
  (2) its sheet again for the still (sheet number = key index // 6), then `tiles.py`, then `set_media.py hybrid`.
- Redeploy: `cd web; python3 -I set_media.py hybrid; ./buildall.sh https://insanelukas.github.io/insanecoaching/ index ../stage16X; ./runall.sh ../stage16X`;
  then `cp -a` to the site clone, commit, push main.
- Clip prompt: since the last 15 clips the first sentence fixes the opening frame ("The video starts exactly on the given image ..."); it helped
  against clips that opened on a tighter framing or with the head out of frame. Use it for any clip made again.
- Scene changes made after a visual check: women's meeting room from the front; women's pull-up park standing (was sitting on the sand);
  women's backstage scene with the robe tied closed (all three ages); women's trophy scene in a jacket and leggings; ma-stage-room is a gallery opening.
- Waiting: `sleep` up to ~44 s inside a sandbox call works; longer calls fail at the gateway. A video job that stays "in progress" for 25 minutes
  is made again (`IDX -`, then `next 1 vid`).
- The media workflow (`.github/workflows/media.yml`, switched on 2026-11-24 with the owner's yes): on this branch only; runs `media/build.py out`
  on a GitHub runner (which can read the result addresses) and commits `out/vid` and `out/done.json` here. It starts only when the workflow file
  or `ci/media.run` changes, so pushing the generation log does not start it. First run: 5 minutes, 180 clips, 61 MB
  (loops 480 x 640, median 0.17 MB; scenes 832 x 624, median 0.34 MB; H.264, 24 fps, no sound, quick start).
- Measured on the live site (man 30-44, all five characters shown, then the end scene): 1.6 MB of quiz media, was 9.9 MB with the service's files.
