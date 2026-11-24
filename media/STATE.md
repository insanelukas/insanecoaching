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

## Status and routine (updated 2026-11-24 12:00)

- Live: main has quiz v16 with the `cdn` manifest (commit d8d42d2 = 30 characters + the 25 scenes of men 30-44). Each redeploy: `cd web; python3 -I set_media.py cdn; ./buildall.sh https://insanelukas.github.io/insanecoaching/ index ../stage16X; check16; cp -a to /home/claude/insanecoaching; commit; push main`.
- Order of scene groups: mb (done), ma, wb, mc, wa, wc. Scene stills 2000-2149, clips 4000-4149.
- Faster routine now: in the sandbox `python3 media/gen.py next N [img|vid]` plans the next N jobs and remembers them in `media/plan/pending.json` (sandbox only),
  so ids can be written down later. Locally: append job lines right after a submit, `S` lines after jobs_wait, `A` after looking at a QA sheet; commit + push; the sandbox pulls
  (`git checkout media/ids.txt; git pull`) before it plans clips, because clips need the approved stills.
- Waiting: `sleep` up to ~44 s inside a sandbox call works; longer calls fail at the gateway.
- Small web files are built in the sandbox (`python3 media/build.py ~/ic/out`): about 0.17 MB per character loop, 0.45 MB per scene. They cannot leave the sandbox without
  the owner's yes to one of: the workflow in `ci/media.yml` (not active), or a download through his Mac.
