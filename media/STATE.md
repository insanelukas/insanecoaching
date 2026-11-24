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
