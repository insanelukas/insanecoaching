#!/usr/bin/env python3
"""First frames of the clips as web stills, packed into sheets.

Why: the video model re-renders the scene, so a clip does not open on the still it was made from (see match.py). The page shows a
still under each clip, and a still with another framing jumps when the clip starts. The first frame of the clip itself does not.

  python3 media/frames.py OUT g|s [SHEET ...]     # all sheets of that kind, or only the numbered ones

  OUT/<kind>_<n>.jpg   a sheet of tiles in one column: g (character loops) 720 x 960, 6 per sheet; s (end scenes) 832 x 624, 9 per sheet.
                       Baseline JPEG 4:2:0, at most 500 kB (the sandbox returns up to 512 KiB of pictures per call).
                       Every tile starts on a 16 px boundary, so `jpegtran -crop` cuts tiles out without encoding them again.
                       The JPEG comment holds JSON: {"sheet", "q", "cols", "tile": [w, h], "keys": [...], "jobs": [...]}
                       (a key is null where that clip is not there yet; jobs = the clip each still was taken from).
Sheet n always holds the same keys (key order of gen.gkeys / gen.skeys), so finished sheets stay as they are when new clips arrive.
Prints one line per sheet: file, bytes, quality, tiles filled.
Runs in the Higgsfield sandbox (it can read the result addresses)."""
import json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3MPJSUjilmNLdPB2lfi6BMrs1ga/hf_{stamp}_{job}.mp4"
CACHE = os.path.expanduser("~/ic/cache"); os.makedirs(CACHE, exist_ok=True)
# one column per sheet: a tall strip is shown small to whoever looks at the returned picture, while the file keeps every pixel
KIND = {"g": dict(base=3000, tile=(720, 960), cols=1, rows=6), "s": dict(base=4000, tile=(832, 624), cols=1, rows=9)}
LIMIT = 500000

def frame(i, job, stamp):
    v = os.path.join(CACHE, f"{i}_{job[:8]}.mp4")
    if not os.path.exists(v) or os.path.getsize(v) < 10000:
        if subprocess.run(["curl", "-sf", "--retry", "3", "-o", v, CDN.format(stamp=stamp, job=job)]).returncode: return None
    f0 = v + ".f0.png"
    if not os.path.exists(f0) or os.path.getsize(f0) < 1000:
        if subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-frames:v", "1", f0]).returncode: return None
    return f0

def main():
    out, kind = sys.argv[1], sys.argv[2]; only = set(int(x) for x in sys.argv[3:])
    K = KIND[kind]; w, h = K["tile"]; cols, rows = K["cols"], K["rows"]; per = cols * rows
    J, S, A = gen.load(); keys = gen.gkeys() if kind == "g" else gen.skeys()
    os.makedirs(out, exist_ok=True)
    for n in range(-(-len(keys) // per)):
        if only and n not in only: continue
        sheet = Image.new("RGB", (cols * w, rows * h), "black"); ks, js = [], []
        for t in range(per):
            m = n * per + t; i = K["base"] + m; key = keys[m] if m < len(keys) else None; f0 = None
            ok = key and i in J and i in S and (kind == "g" or (i - 2000) in A)
            if ok: f0 = frame(i, J[i], S[i])
            if f0:
                im = Image.open(f0).convert("RGB")
                # the clips are 3:4 or 4:3 like the tiles; a clip of another shape is centre-cropped to the tile's shape first
                sw, sh = im.size
                if abs(sw * h - sh * w) > 2 * max(w, h):
                    nw = min(sw, sh * w // h); nh = min(sh, sw * h // w); x0 = (sw - nw) // 2; y0 = (sh - nh) // 2
                    im = im.crop((x0, y0, x0 + nw, y0 + nh))
                sheet.paste(im.resize((w, h), Image.LANCZOS), ((t % cols) * w, (t // cols) * h))
            ks.append(key if f0 else None); js.append(J[i] if f0 else None)
        name = f"{kind}_{n}.jpg"; path = os.path.join(out, name)
        if not any(ks):
            if os.path.exists(path): os.remove(path)
            print(name, "empty"); continue
        for q in range(84, 55, -3):
            sheet.save(path, "JPEG", quality=q, subsampling="4:2:0", optimize=True, progressive=False)
            if os.path.getsize(path) <= LIMIT - 2000: break
        # the comment segment goes after the JFIF header (written by hand so it does not depend on the Pillow version)
        note = json.dumps(dict(sheet=name[:-4], q=q, cols=cols, tile=[w, h], keys=ks, jobs=js), separators=(",", ":")).encode()
        b = open(path, "rb").read(); assert b[:2] == b"\xff\xd8" and len(note) < 65000
        at = 4 + int.from_bytes(b[4:6], "big") if b[2:4] == b"\xff\xe0" else 2
        open(path, "wb").write(b[:at] + b"\xff\xfe" + (len(note) + 2).to_bytes(2, "big") + note + b[at:])
        print(name, os.path.getsize(path), "q", q, "tiles", sum(1 for k in ks if k))

if __name__ == "__main__":
    main()
