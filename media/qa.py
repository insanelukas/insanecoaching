#!/usr/bin/env python3
"""Contact sheets for visual checks, run in the Higgsfield sandbox.
  python3 media/qa.py FIRST LAST [PER_SHEET]   # indexes FIRST..LAST inclusive -> ~/ic/qa/sheet_<first>_<n>.jpg
Stills: one thumbnail each. Videos (3000+): first, middle and last frame side by side.
ids.txt lines: "<index> <job_id> <YYYYMMDD_HHMMSS>"; the last line for an index wins.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3MPJSUjilmNLdPB2lfi6BMrs1ga/hf_{stamp}_{job}.{ext}"
CACHE = os.path.expanduser("~/ic/cache"); QA = os.path.expanduser("~/ic/qa")
os.makedirs(CACHE, exist_ok=True); os.makedirs(QA, exist_ok=True)
keys = json.load(open(os.path.join(HERE, "plan", "keys.json")))
def key(i):
    return keys["g"][i % 1000] if (i // 1000) in (1, 3) else keys["s"][i % 1000]
sys.path.insert(0, HERE)
import gen
def ids():
    J, S, A = gen.load()
    return {i: (J[i], S[i]) for i in J if i in S}
def fetch(i, job, stamp):
    ext = "mp4" if i >= 3000 else "png"
    f = os.path.join(CACHE, f"{i}_{job[:8]}.{ext}")
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        r = subprocess.run(["curl", "-sf", "-o", f, CDN.format(stamp=stamp, job=job, ext=ext)])
        if r.returncode: return None
    return f
def thumb(i, f, w, h):
    if i >= 3000:
        n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip() or 121)
        out = f + ".strip.jpg"
        sel = f"eq(n,0)+eq(n,{n // 2})+eq(n,{n - 1})"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", f"select='{sel}',scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,tile=3x1", "-frames:v", "1", "-q:v", "5", out])
        return Image.open(out).convert("RGB")
    im = Image.open(f).convert("RGB"); im.thumbnail((w, h)); bg = Image.new("RGB", (w, h), "black"); bg.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return bg
def main():
    if sys.argv[1] == "LIST":
        want = [int(x) for x in sys.argv[2].split(",")]; first = want[0]; sys.argv = [sys.argv[0], "0", "0"] + sys.argv[3:]
    else:
        first, last = int(sys.argv[1]), int(sys.argv[2]); want = list(range(first, last + 1))
    J = ids()
    video = first >= 3000; portrait = (first // 1000) in (1, 3)
    per = int(sys.argv[3]) if len(sys.argv) > 3 else (4 if video else 8)
    w, h = (150, 200) if portrait else (160, 120)
    if not video: w, h = (210, 280) if portrait else ((228, 171) if per > 9 else (300, 225))
    cells = []
    for i in want:
        if i not in J: continue
        f = fetch(i, *J[i])
        if not f: print("fetch failed", i); continue
        t = thumb(i, f, w, h); d = ImageDraw.Draw(t); lab = f"{i} {key(i)}"
        d.rectangle((0, 0, 8 + 7 * len(lab), 16), fill="black"); d.text((4, 2), lab, fill="yellow"); cells.append(t)
    cols = 2 if video else (4 if portrait or per > 9 else 3)
    sheets = []
    for s in range(0, len(cells), per):
        chunk = cells[s:s + per]; cw, ch = chunk[0].size; rows = -(-len(chunk) // cols)
        sh = Image.new("RGB", (cols * cw + (cols - 1) * 4, rows * ch + (rows - 1) * 4), "black")
        for k, c in enumerate(chunk): sh.paste(c, ((k % cols) * (cw + 4), (k // cols) * (ch + 4)))
        out = os.path.join(QA, f"sheet_{first}_{s // per}.jpg"); sh.save(out, quality=78); sheets.append((out, os.path.getsize(out)))
    print(json.dumps(sheets))
main()
