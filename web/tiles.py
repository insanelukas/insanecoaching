# tiles.py [DIR]: cuts the stills out of the sheets made by media/frames.py (branch media-build) and files them under ./media-out.
#   DIR   where the sheets are (default: this session's tool results, where the pictures a sandbox call returns are kept).
#         A sheet is any .jpg whose JPEG comment is the JSON frames.py writes; of two sheets with the same name the newer wins.
#   media-out/img/g/<key>.jpg   character loop, first frame, 720 x 960
#   media-out/img/s/<key>.jpg   end scene, first frame, 832 x 624
#   media-out/stills.json       "g:<key>" / "s:<key>" -> the clip job the still was taken from (set_media.py uses a still only for that clip)
# The tiles are cut with jpegtran -crop on 16 px boundaries, so they are not encoded a second time.
import glob, json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/root/.claude/projects/-home-claude/2c8c76ce-a1e5-5754-8a50-aebf3aa141d1/tool-results'
JT = os.environ.get('JPEGTRAN') or os.path.join(HERE, '..', 'jt', 'node_modules', '.bin', 'jpegtran')
OUT = os.path.join(HERE, 'media-out'); DJ = os.path.join(OUT, 'stills.json')
done = json.load(open(DJ)) if os.path.exists(DJ) else {}
sheets = {}
for f in sorted(glob.glob(os.path.join(SRC, '*.jpg')), key=os.path.getmtime):
    try:
        c = Image.open(f).info.get('comment')
        d = json.loads(c.decode() if isinstance(c, bytes) else c) if c else None
    except Exception:
        d = None
    if isinstance(d, dict) and 'sheet' in d and 'keys' in d: sheets[d['sheet']] = (f, d)
made = same = 0; total = 0
for name in sorted(sheets, key=lambda s: (s[0], int(s[2:]))):
    f, d = sheets[name]; kind = name[0]; w, h = d['tile']; cols = d['cols']
    W, H = Image.open(f).size; assert W % w == 0 and H % h == 0 and w % 16 == 0 and h % 16 == 0, (name, W, H)
    os.makedirs(os.path.join(OUT, 'img', kind), exist_ok=True)
    for t, (key, job) in enumerate(zip(d['keys'], d['jobs'])):
        if not key: continue
        p = os.path.join(OUT, 'img', kind, key + '.jpg')
        if done.get(kind + ':' + key) == job and os.path.exists(p): same += 1; continue
        x, y = (t % cols) * w, (t // cols) * h
        subprocess.run([JT, '-crop', '%dx%d+%d+%d' % (w, h, x, y), '-copy', 'none', '-optimize', '-progressive', '-outfile', p, f], check=True)
        assert Image.open(p).size == (w, h), (key, Image.open(p).size)
        done[kind + ':' + key] = job; made += 1; total += os.path.getsize(p)
    print(name, 'q', d['q'], os.path.getsize(f), 'bytes', sum(1 for k in d['keys'] if k), 'tiles', os.path.basename(f))
json.dump(done, open(DJ, 'w'), indent=0, sort_keys=True)
print('sheets', len(sheets), 'tiles made', made, 'unchanged', same, 'new bytes', total, 'stills on file', len(done))
