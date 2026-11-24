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

## Status and routine (updated 2026-11-24 15:00 Vilnius time)

- Done: 30 character loops and 150 end scenes (25 per group: mb, ma, wb, mc, wa, wc), every still and clip looked at on contact sheets.
- Found on the way: the video model re-renders the scene, so a clip does NOT open on the still it was made from (`media/match.py` measures it;
  all 156 clips measured differed, many open on a tighter framing). The page shows a still under each clip, so the site now uses each clip's own
  first frame as its still: `media/frames.py` packs the first frames into sheets (one column, at most 500 kB), a sandbox call returns a sheet as a
  picture, `web/tiles.py` cuts the tiles out with `jpegtran -crop` (no second encoding) into `web/media-out/img/g|s/<key>.jpg` and notes in
  `media-out/stills.json` which clip each still belongs to.
- Site media list: `python3 -I set_media.py hybrid` = clips at the Higgsfield result addresses, stills as files of the site (`img/g`, `img/s`).
  A clip made again needs its sheet again (sheet number = key index // 6), then `tiles.py`, then `set_media.py hybrid`; until then that key falls
  back to the service's copy of the generated still.
- Redeploy: `cd web; python3 -I set_media.py hybrid; ./buildall.sh https://insanelukas.github.io/insanecoaching/ index ../stage16X; ./runall.sh ../stage16X`;
  then `cp -a` to the site clone, commit, push main.
- Clip prompt: since the last 15 clips the first sentence fixes the opening frame ("The video starts exactly on the given image ..."); it helped
  against clips that opened on a tighter framing or with the head out of frame. Use it for any clip made again.
- Scene changes made after a visual check: women's meeting room from the front; women's pull-up park standing (was sitting on the sand);
  women's backstage scene with the robe tied closed (all three ages); women's trophy scene in a jacket and leggings; ma-stage-room is a gallery opening.
- Waiting: `sleep` up to ~44 s inside a sandbox call works; longer calls fail at the gateway. A video job that stays "in progress" for 25 minutes
  is made again (`IDX -`, then `next 1 vid`).
- Still open: the clips themselves are the service's full-size files (about 1.3 MB per loop, up to 2 MB per scene). Small web files are built in
  the sandbox (`python3 media/build.py ~/ic/out`: about 0.17 MB per loop, 0.45 MB per scene) but cannot leave it without the owner's yes to one of:
  the workflow in `ci/media.yml` (not active), or a download through his Mac. (Pictures can leave through the sandbox's picture return; clips cannot.)
