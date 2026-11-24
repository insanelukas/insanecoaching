#!/usr/bin/env python3
"""Web files from the generation results.

  python3 media/build.py OUT [--only g|s] [--keys k1,k2] [--jobs 4]

  OUT/vid/g/<key>.mp4, OUT/img/g/<key>.jpg   character loop and its first frame, 480 x 640
  OUT/vid/s/<key>.mp4, OUT/img/s/<key>.jpg   end scene and its first frame, 832 x 624
  OUT/done.json                              key -> job id of the clip the files were made from (unchanged keys are skipped)

A character needs a finished loop; a scene needs a finished clip whose still was approved. H.264, no sound, quick start.
Runs anywhere that can read the result addresses and has ffmpeg (the Higgsfield sandbox, a GitHub runner).
"""
import concurrent.futures, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3MPJSUjilmNLdPB2lfi6BMrs1ga/hf_{stamp}_{job}.mp4"
SIZE = {"g": (480, 640, 27), "s": (832, 624, 27)}   # width, height, crf

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd[:6]) + " ... " + r.stderr[-300:])

def one(kind, key, job, stamp, out, cache):
    w, h, crf = SIZE[kind]
    src = os.path.join(cache, f"{job}.mp4")
    if not os.path.exists(src) or os.path.getsize(src) < 10000:
        run(["curl", "-sf", "--retry", "3", "-o", src, CDN.format(stamp=stamp, job=job)])
    v = os.path.join(out, "vid", kind, key + ".mp4"); p = os.path.join(out, "img", kind, key + ".jpg")
    vf = f"scale={w}:{h}:flags=lanczos,setsar=1"
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", vf, "-r", "24", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", str(crf),
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", v])
    # the still is the first frame of the encoded clip, so the page can cross-fade between the two without a jump
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-frames:v", "1", "-q:v", "4", p])
    return key, os.path.getsize(v), os.path.getsize(p)

def main():
    out = sys.argv[1]; arg = sys.argv[2:]
    only = arg[arg.index("--only") + 1] if "--only" in arg else ""
    keys = set(arg[arg.index("--keys") + 1].split(",")) if "--keys" in arg else None
    jobs = int(arg[arg.index("--jobs") + 1]) if "--jobs" in arg else 4
    J, S, A = gen.load(); G, SK = gen.gkeys(), gen.skeys()
    cache = os.path.join(out, ".cache"); os.makedirs(cache, exist_ok=True)
    for a in ("vid", "img"):
        for k in ("g", "s"): os.makedirs(os.path.join(out, a, k), exist_ok=True)
    dj = os.path.join(out, "done.json"); done = json.load(open(dj)) if os.path.exists(dj) else {}
    todo = []
    for kind, names, base in (("g", G, 3000), ("s", SK, 4000)):
        if only and only != kind: continue
        for n, key in enumerate(names):
            i = base + n
            if keys is not None and key not in keys: continue
            if i not in J or i not in S: continue
            if kind == "s" and (i - 2000) not in A: continue
            if done.get(kind + ":" + key) == J[i] and os.path.exists(os.path.join(out, "vid", kind, key + ".mp4")): continue
            todo.append((kind, key, J[i], S[i]))
    tot = [0, 0]; bad = []
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        fs = {ex.submit(one, k, key, job, st, out, cache): (k, key, job) for k, key, job, st in todo}
        for f in concurrent.futures.as_completed(fs):
            k, key, job = fs[f]
            try:
                _, a, b = f.result(); done[k + ":" + key] = job; tot[0] += a; tot[1] += b
            except Exception as e: bad.append((key, str(e)[:200]))
    json.dump(done, open(dj, "w"), indent=0, sort_keys=True)
    print(json.dumps(dict(made=len(todo) - len(bad), failed=bad, total=len(done), clip_bytes=tot[0], still_bytes=tot[1])))
    if bad: sys.exit(1)
if __name__ == "__main__":
    main()
