#!/usr/bin/env python3
"""Does each clip open on its still? The page shows the still under the clip, so a clip that opens on another framing jumps.

  python3 media/match.py [FIRST LAST]     # default 4000 4149 (end scenes); 3000 3029 for the character loops

Prints the mean absolute difference (0-255, grey, 96 px) between the still as the page shows it and the clip's first frame,
worst first, then the index and key. About 1-4 is the same picture; above ~10 the clip was re-framed and should be made again.
For loops (3000+) a second number compares the last frame with the first.
Runs in the Higgsfield sandbox (it can read the result addresses)."""
import os, subprocess, sys
from PIL import Image, ImageChops, ImageStat
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3MPJSUjilmNLdPB2lfi6BMrs1ga/hf_{stamp}_{job}{suffix}"
CACHE = os.path.expanduser("~/ic/cache"); os.makedirs(CACHE, exist_ok=True)

def get(name, url):
    f = os.path.join(CACHE, name)
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        if subprocess.run(["curl", "-sf", "--retry", "2", "-o", f, url]).returncode: return None
    return f

def diff(a, b, size):
    x = Image.open(a).convert("L").resize(size); y = Image.open(b).convert("L").resize(size)
    return round(ImageStat.Stat(ImageChops.difference(x, y)).mean[0], 1)

def main():
    a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (4000, 4149)
    J, S, A = gen.load(); G, SK = gen.gkeys(), gen.skeys(); out = []
    for i in range(a, b + 1):
        s = i - 2000
        if i not in J or i not in S or s not in J or s not in S: continue
        v = get(f"{i}_{J[i][:8]}.mp4", CDN.format(stamp=S[i], job=J[i], suffix=".mp4"))
        p = get(f"{s}_{J[s][:8]}_min.webp", CDN.format(stamp=S[s], job=J[s], suffix="_min.webp"))
        if not v or not p: print("fetch failed", i); continue
        f0 = v + ".f0.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-frames:v", "1", f0])
        loop = i < 4000; size = (72, 96) if loop else (96, 72)
        row = [diff(f0, p, size)]
        if loop:
            f1 = v + ".f1.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.2", "-i", v, "-update", "1", "-q:v", "2", f1])
            row.append(diff(f0, f1, size))
        out.append((row, i, (G if loop else SK)[i % 1000]))
    out.sort(reverse=True)
    for row, i, key in out: print(*row, i, key)

if __name__ == "__main__":
    main()
