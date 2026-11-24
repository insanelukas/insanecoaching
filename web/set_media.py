# set_media.py MODE [IDS]: writes the MEDIA line of insane-coaching.html from the generation log (ids.txt of the media work branch).
#   cdn    clips and stills straight from the Higgsfield result addresses (stills: the service's own smaller .webp copy)
#   hybrid clips from the Higgsfield result addresses, stills from this site: media-out/img/g|s/<key>.jpg, the first frame of that very
#          clip (tiles.py files them; stills.json says which clip each was taken from). The video model re-renders the scene, so a clip
#          does not open on the still it was generated from; its own first frame is the still that does not jump. A key without such a
#          still falls back to the service's copy of the generated still, as in cdn.
#   local  files in this site: vid/g, vid/s, img/g, img/s (only the keys whose files exist under ./media-out)
#   none   empty: no generated pictures
import io, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1]; GEN = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/ic-media/media'
sys.path.insert(0, GEN); import gen
J, S, A = gen.load(); G, SK = gen.gkeys(), gen.skeys()
CDN = 'https://d8j0ntlcm91z4.cloudfront.net/user_3MPJSUjilmNLdPB2lfi6BMrs1ga/'
# where the site's own files are when the page itself does not know (the preview); a built page uses its own address
LIVE = os.environ.get('SITE_BASE', 'https://insanelukas.github.io/insanecoaching/')
M = dict(base='', g={}, s={})
if MODE in ('cdn', 'hybrid'):
    M['base'] = CDN
    out = os.path.join(HERE, 'media-out'); own = {}; n_own = 0
    if MODE == 'hybrid':
        M['site'] = LIVE
        own = json.load(io.open(os.path.join(out, 'stills.json'), encoding='utf-8'))
    f = lambda i, ext: 'hf_%s_%s%s' % (S[i], J[i], ext) if i in S and i in J else ''
    def still(kind, k, i, gen_still):
        # the clip's own first frame when it is on file for the clip in use
        global n_own
        p = 'img/%s/%s.jpg' % (kind, k)
        if i in S and own.get(kind + ':' + k) == J.get(i) and os.path.exists(os.path.join(out, p)): n_own += 1; return p
        return f(gen_still, '_min.webp')
    for n, k in enumerate(G):
        v, p = f(3000 + n, '.mp4'), still('g', k, 3000 + n, 1000 + n)
        if v or p: M['g'][k] = [v, p]
    for n, k in enumerate(SK):
        v, p = f(4000 + n, '.mp4'), still('s', k, 4000 + n, 2000 + n)
        if v and p and (2000 + n) in A: M['s'][k] = [v, p]
    if MODE == 'hybrid': print('stills of this site', n_own, 'of', len(M['g']) + len(M['s']))
elif MODE == 'local':
    out = os.path.join(HERE, 'media-out')
    for kind, keys in (('g', G), ('s', SK)):
        for k in keys:
            v, p = 'vid/%s/%s.mp4' % (kind, k), 'img/%s/%s.jpg' % (kind, k)
            hv, hp = os.path.exists(os.path.join(out, v)), os.path.exists(os.path.join(out, p))
            if (hv or hp) if kind == 'g' else (hv and hp): M[kind][k] = [v if hv else '', p if hp else '']
elif MODE == 'test':
    # every key, on the same host as the real ones, so a test can answer the requests itself; TEST_SKIP=prefix,prefix leaves keys out
    M['base'] = 'https://d8j0ntlcm91z4.cloudfront.net/test/'
    skip = [x for x in os.environ.get('TEST_SKIP', '').split(',') if x]
    for kind, keys in (('g', G), ('s', SK)):
        for k in keys:
            if any((kind + ':' + k).startswith(x) for x in skip): continue
            M[kind][k] = ['%s/%s.mp4' % (kind, k), '%s/%s.webp' % (kind, k)]
OUTF = os.environ.get('MEDIA_OUT')
P = os.path.join(HERE, 'insane-coaching.html'); s = io.open(P, encoding='utf-8').read()
s, n = re.subn(r'(?m)^  var MEDIA = \{.*\};$', lambda m: '  var MEDIA = ' + json.dumps(M, separators=(',', ':')) + ';', s)
assert n == 1, n
if OUTF:
    # a test copy of the preview with this manifest; the source file stays as it is
    i = s.index('</style>') + len('</style>')
    s = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + s[:i] + '\n</head>\n<body>\n' + s[i:] + '\n</body>\n</html>\n'
    io.open(os.path.join(HERE, OUTF), 'w', encoding='utf-8').write(s)
else:
    io.open(P, 'w', encoding='utf-8').write(s)
print(MODE, 'characters', len(M['g']), 'scenes', len(M['s']), 'bytes', len(json.dumps(M)))
