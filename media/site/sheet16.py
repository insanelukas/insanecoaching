# sheet16.py DIR OUT [COLS] [WIDTH]: one contact sheet of the screenshots in DIR
import sys, os
from PIL import Image
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6; w = int(sys.argv[4]) if len(sys.argv) > 4 else 260
fs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
ims = []
for f in fs:
    im = Image.open(os.path.join(d, f)).convert('RGB'); im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS); ims.append(im)
h = max(i.height for i in ims); rows = -(-len(ims) // cols)
sh = Image.new('RGB', (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
for k, im in enumerate(ims): sh.paste(im, ((k % cols) * (w + 6), (k // cols) * (h + 6)))
sh.save(out, quality=82); print(out, sh.size, os.path.getsize(out))
