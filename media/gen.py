#!/usr/bin/env python3
"""Prompt plan for the game-style quiz characters (30) and the personalised end scenes (150).

Usage:
  python3 media/gen.py plan                 # writes media/plan/*.json (batches of 12) and media/plan/keys.json
  python3 media/gen.py batch NAME IDX...    # writes media/plan/NAME.json with just these indexes (retries)
Indexes: 1000+ roster still, 2000+ scene still, 3000+ roster video, 4000+ scene video.
Job ids come from media/ids.txt: "<index> <job_id> [HHMMSS]" (the last line for an index wins).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = ("Stylized photoreal AAA open-world video game character, next-gen console in-engine cinematic render, crisp detail, "
         "slightly heightened contrast and saturation, warm golden-hour light with teal shadows, subtle film grain.")
STYLE_REF = "same stylized photoreal AAA open-world video game in-engine cinematic look, warm golden-hour light with teal shadows, subtle film grain"
NEG = "No text, no lettering, no logos, no watermark, no game UI."
GOALS = ["fat", "athletic", "muscle", "hybrid", "stage"]
WHYS = ["kids", "room", "respect", "self", "health"]
ORDER = [("m", "b"), ("m", "a"), ("w", "b"), ("m", "c"), ("w", "a"), ("w", "c")]
YEARS = {"a": 26, "b": 38, "c": 52}
PR = {"m": dict(n="man", He="He", he="he", his="his", him="him", His="His"),
      "w": dict(n="woman", He="She", he="she", his="her", him="her", His="Her")}
BUILD = {
 "m": {"fat": "slim, lean and fit build with a flat stomach and light muscle tone",
       "athletic": "athletic V-shaped build with clear muscle definition",
       "muscle": "big muscular strength build with thick arms, a wide chest and a broad back",
       "hybrid": "hybrid athlete build, muscular yet lean, with strong legs",
       "stage": "competition bodybuilder physique, very lean and very muscular"},
 "w": {"fat": "slim, lean and fit build with a flat stomach and light muscle tone",
       "athletic": "athletic toned build with defined shoulders, arms and legs",
       "muscle": "strong, firm athletic build with shapely legs and toned arms",
       "hybrid": "hybrid athlete build, strong and lean, with powerful legs and shoulders",
       "stage": "fitness competitor physique, lean, toned and athletic"}}
LOOK = {
 "m": {"fat": "short {hc} hair, clean-shaven", "athletic": "short {hc} hair, light stubble", "muscle": "very short {hc} hair, short beard",
       "hybrid": "short {hc} hair with a fade, short beard", "stage": "slicked-back {hc} hair, clean-shaven, deep tan"},
 "w": {"fat": "{hc} hair in a ponytail", "athletic": "{hc} hair in a braid", "muscle": "long {hc} hair in a high ponytail",
       "hybrid": "{hc} hair in a high ponytail", "stage": "sleek {hc} hair pulled back, deep tan"}}
HC = {"m": {"fat": "brown", "athletic": "dark-blond", "muscle": "light-brown", "hybrid": "dark", "stage": "dark"},
      "w": {"fat": "dark-brown", "athletic": "auburn", "muscle": "dark", "hybrid": "blond", "stage": "dark-blond"}}
OUTFIT = {
 "m": {"fat": "a fitted sleeveless running top, running shorts and running shoes",
       "athletic": "black training shorts and training shoes, shirtless",
       "muscle": "a fitted grey t-shirt with rolled sleeves, black training shorts and training shoes",
       "hybrid": "a black weighted vest over a fitted black t-shirt, training shorts and trail running shoes",
       "stage": "black posing trunks, barefoot"},
 "w": {"fat": "a sports top, high-waisted running shorts and running shoes",
       "athletic": "a sports top, training shorts and training shoes",
       "muscle": "a sports top, high-waisted training leggings and lifting shoes",
       "hybrid": "a black weighted vest over a sports top, high-waisted training leggings and trail running shoes",
       "stage": "a sparkling two-piece fitness competition suit and clear high heels"}}
POSE = {
 "fat": "skipping rope mid-jump with the rope arcing overhead, on a seaside promenade at sunset with palm trees and a calm sea behind",
 "athletic": "hanging from an outdoor pull-up bar with arms fully extended and feet off the ground, at a beach workout park at sunset with palm trees and the sea behind",
 "muscle_m": "standing tall holding two heavy dumbbells at his sides in a gritty industrial warehouse gym with warm sunset light through tall windows",
 "muscle_w": "standing tall with a loaded barbell across her upper back in front of a squat rack in a gritty industrial warehouse gym with warm sunset light through tall windows",
 "hybrid": "standing in an athletic ready stance beside a wooden plyo box on a rooftop training area at sunset, a city skyline and palm trees behind",
 "stage": "standing in a relaxed, confident front pose on a fitness competition stage under warm spotlights, a dark audience hall behind and light haze in the air"}
MOVE = {
 "fat": "{He} skips rope at a quick steady rhythm, light on {his} feet, the rope whipping around; shoulders relaxed, breathing easy.",
 "athletic": "{He} does two smooth strict pull-ups, chin over the bar each time, lowers under control and returns to the exact dead hang.",
 "muscle_m": "He curls both dumbbells up to his shoulders with controlled power, squeezes his biceps at the top, then lowers them slowly back to his sides and returns to the exact starting stance.",
 "muscle_w": "She squats down under control until her thighs are parallel to the floor and drives back up to standing, twice, the barbell steady across her upper back, and returns to the exact starting stance.",
 "hybrid": "{He} bursts into a fast high-knees sprint on the spot for a few seconds, arms pumping hard, the weighted vest bouncing slightly, then slows down and settles back into the exact starting stance.",
 "stage_m": "He raises both arms into a front double-biceps pose, holds it flexed for a moment, then relaxes back to the exact starting pose while the spotlights shimmer.",
 "stage_w": "She turns a quarter to the side with one hand on her hip in a confident stage pose, holds it, then turns back to the exact starting pose while the spotlights shimmer."}
KIDS = "{his} two children, a boy about 8 and a girl about 6 in casual clothes"
SC = {
 "fat": {
  "kids": dict(m="a fitted t-shirt and shorts", w="a fitted t-shirt and leggings",
    scene="A green city park at golden hour. {He} runs across the grass holding a kite string, with " + KIDS + ", running beside {him} and laughing; the children are seen from the side or from behind; a colourful kite flies above.",
    move="{He} runs across the grass holding the kite string while the two children run beside {him}; the kite tugs in the wind and the camera tracks alongside."),
  "room": dict(m="a slim-fit navy suit with an open-collar white shirt", w="an elegant fitted knee-length dress",
    scene="A rooftop evening party at sunset with string lights and a city view. {He} walks in with an easy, confident smile while guests holding drinks turn their heads toward {him}.",
    move="{He} walks through the party toward the camera with an easy, confident smile; several guests turn their heads to look; the camera glides backward in front of {him}."),
  "respect": dict(m="a sleeveless running top and running shorts", w="a running top and running shorts",
    scene="The finish line of a city road race at sunset under a plain arch without any lettering. {He} has just crossed the line and a friend gives {him} a high-five while spectators behind the barriers clap.",
    move="{He} crosses the finish line, slows to a walk, smiles and high-fives a friend; the spectators clap."),
  "self": dict(m="well-fitting jeans and a fitted t-shirt", w="well-fitting jeans and a fitted top",
    scene="A bright bedroom in morning light with a tall standing mirror. {He} stands in front of the mirror tightening {his} belt one notch and smiles at {his} reflection.",
    move="{He} tightens the belt one notch, turns slightly to check the mirror and smiles, pleased."),
  "health": dict(m="a light running jacket and running shorts", w="a light running jacket and running tights",
    scene="A tree-lined park path at sunrise. {He} jogs at an easy pace with a happy golden retriever running beside {him}.",
    move="{He} jogs along the path at an easy pace while the dog runs happily beside {him}; the camera tracks in front of them.")},
 "athletic": {
  "kids": dict(m="a fitted t-shirt and shorts", w="a fitted t-shirt and shorts",
    scene="A backyard lawn at sunset with a small football goal. {He} plays football with " + KIDS + ", dribbling the ball past them as they chase {him}; the children are seen from the side or from behind.",
    move="{He} dribbles the football past the two children, turns and passes it gently to the boy; everyone is laughing."),
  "room": dict(m="a fitted light-blue dress shirt with the sleeves rolled up and tailored trousers", w="a fitted sleeveless blouse and tailored trousers",
    scene="A bright modern open-plan office with large windows. {He} walks through the office with confident posture while colleagues at their desks look up at {him}.",
    move="{He} walks through the office with confident posture; colleagues look up from their desks as {he} passes; the camera glides backward in front of {him}."),
  "respect": dict(m="black training shorts, shirtless", w="a sports top and training shorts",
    scene="An outdoor beach workout park at sunset. {He} has just dropped from the pull-up bar and a training partner gives {him} a fist bump, impressed, while two others nod.",
    move="{He} drops from the pull-up bar, exhales and bumps fists with a training partner who nods, impressed."),
  "self": dict(m="training shorts, shirtless, with a towel over one shoulder", w="a sports top and leggings, with a towel over one shoulder",
    scene="A clean gym locker room with a large mirror. After a workout {he} looks at {his} reflection and gives a small satisfied nod.",
    move="{He} wipes {his} face with the towel, looks at {his} reflection in the mirror and gives a small satisfied nod."),
  "health": dict(m="a cycling jersey, cycling shorts and a helmet", w="a cycling jersey, cycling shorts and a helmet",
    scene="A coastal bike path at sunrise beside the sea. {He} rides a road bike at a strong, steady pace.",
    move="{He} rides the road bike along the coast at a strong steady pace, legs spinning smoothly; the camera tracks beside {him}.")},
 "muscle": {
  "kids": dict(m="a fitted t-shirt and shorts", w="a fitted t-shirt and denim shorts",
    scene_m="A beach boardwalk at sunset. He walks toward the camera carrying his daughter, about 6, on his shoulders and holding the hand of his son, about 8; both children are laughing.",
    scene_w="A beach boardwalk at sunset. She walks toward the camera giving her son, about 6, a piggyback ride while her daughter, about 8, skips beside her holding her hand; both children are laughing.",
    move="{He} walks toward the camera with the child riding up high, bouncing playfully; the other child skips alongside, laughing."),
  "room": dict(m="a fitted white dress shirt with the sleeves rolled up and dark trousers", w="a fitted sleeveless top and tailored trousers",
    scene_m="A modern glass-walled meeting room high above a coastal city. Seen from behind, he walks toward the head of the table, his broad shoulders, thick forearms and V-shaped back clearly visible, while four seated colleagues in business clothes turn their heads to look at him.",
    scene_w="A modern glass-walled meeting room high above a coastal city. She walks toward the head of the table with strong posture, her toned arms and shoulders visible, while four seated colleagues in business clothes turn their heads to look at her.",
    move="{He} walks toward the head of the table and places {his} hands on it; the seated colleagues turn their heads to look at {him}."),
  "respect": dict(m="a fitted grey t-shirt and black training shorts", w="a sports top and high-waisted leggings",
    scene="A gritty industrial warehouse gym. {He} stands tall at the top of a heavy barbell deadlift while three gym members behind {him} watch and clap.",
    move="{He} holds the heavy barbell at a strong lockout, lowers it under control and stands tall; the gym members behind {him} clap."),
  "self": dict(m="jeans and a fitted t-shirt whose sleeves hug his arms", w="a fitted dress",
    scene="A stylish clothing shop fitting area with a large mirror and warm light. {He} looks at {his} reflection, adjusts the fit and smiles with quiet pride.",
    move="{He} adjusts the fit of the clothes, turns slightly in front of the mirror and smiles with quiet pride."),
  "health": dict(m="a fitted t-shirt, hiking shorts, a backpack and trail shoes", w="a fitted t-shirt, hiking shorts, a backpack and trail shoes",
    scene="A hill trail above a coastal city at sunrise. {He} hikes uphill at a strong pace, breathing easily.",
    move="{He} hikes steadily up the trail at a strong pace, breathing easily; the camera tracks in front of {him}.")},
 "hybrid": {
  "kids": dict(m="a fitted grey t-shirt and shorts", w="a fitted t-shirt and leggings",
    scene="A suburban driveway with a basketball hoop above the garage door at sunset. {He} laughs as {he} dribbles a basketball past " + KIDS + ", who chase {him}; the children are seen from the side or from behind.",
    move="{He} dribbles past the two children, spins and lays the ball up into the hoop; the kids jump and cheer."),
  "room": dict(m="a linen shirt with the sleeves rolled up and chinos", w="a light fitted summer dress",
    scene="A beach club terrace at sunset. {He} arrives with a relaxed smile; friends at a table wave and people nearby glance over at {him}.",
    move="{He} walks onto the terrace with a relaxed smile and waves back at friends at a table; people nearby glance over."),
  "respect": dict(m="a fitted training t-shirt and shorts, with a finisher medal around his neck", w="a sports top and leggings, with a finisher medal around her neck",
    scene="The finish area of an indoor fitness race with sleds and rowing machines in the background. {He} stands catching {his} breath while another competitor shakes {his} hand and pats {his} shoulder.",
    move="{He} catches {his} breath, smiles and shakes hands with another competitor who pats {his} shoulder."),
  "self": dict(m="a fitted t-shirt and training shorts", w="a sports top and leggings",
    scene="An empty rooftop training area at sunrise above the city. Alone, {he} stands with hands on hips after a workout, taking a deep breath and looking out over the city, content.",
    move="{He} finishes a stretch, puts {his} hands on {his} hips, takes a deep breath and looks out over the city, content."),
  "health": dict(m="a trail running vest, a t-shirt and shorts", w="a trail running vest, a top and shorts",
    scene="A coastal ridge trail at sunrise with the sea far below. {He} runs along the trail with light, strong strides.",
    move="{He} runs along the ridge trail with light, strong strides; the camera tracks beside {him} as the sun rises over the sea.")},
 "stage": {
  "kids": dict(m="jeans and a fitted t-shirt, with a gold medal around his neck", w="jeans and a fitted top, with a gold medal around her neck",
    scene="A bright living room at sunset with a trophy on the shelf. {He} flexes one arm playfully while " + KIDS + ", copy the pose beside {him}, flexing their arms and laughing.",
    move="{He} flexes one arm, the two children copy the pose and giggle; {he} laughs and ruffles the boy's hair."),
  "room": dict(m="a tailored black tuxedo that fits his broad shoulders", w="an elegant long evening gown that shows her toned shoulders and arms",
    scene="A gala evening in a grand hotel lobby with warm lights. {He} walks down a wide staircase while guests below look up at {him}.",
    move="{He} walks down the wide staircase with calm confidence; guests below look up and a few smile."),
  "respect": dict(m="black posing trunks", w="a sparkling two-piece fitness competition suit",
    scene="A fitness competition stage under warm spotlights. A judge in a suit hands {him} a gold trophy and shakes {his} hand while the audience applauds in the dark hall.",
    move="{He} accepts the gold trophy from the judge, shakes hands and raises the trophy slightly; the audience applauds."),
  "self": dict(m="a black robe open over posing trunks", w="a satin robe over her competition suit",
    scene="A backstage dressing room with a mirror framed by warm bulbs. {He} looks at {his} reflection before stepping on stage, focused and proud.",
    move="{He} looks at {his} reflection, takes a slow breath, gives a small confident nod and turns toward the stage door."),
  "health": dict(m="a fitted t-shirt and joggers", w="a fitted top and leggings",
    scene="A bright modern kitchen in the morning. {He} plates a colourful healthy meal of chicken, rice and vegetables at the counter, looking energetic.",
    move="{He} finishes plating the colourful meal, picks up a fork and takes a bite with an energetic smile.")}}

def gkeys():
    return [f"{s}{a}-{g}" for s, a in ORDER for g in GOALS]
def skeys():
    return [f"{s}{a}-{g}-{w}" for s, a in ORDER for g in GOALS for w in WHYS]
def hair(sex, goal, age):
    c = HC[sex][goal]
    if age == "c":
        c = ("grey-flecked " + c) if sex == "m" else (c + ", lightly silver-streaked")
    look = LOOK[sex][goal].format(hc=c)
    if age == "c":
        look += ", a few lines on his face" if sex == "m" else ", fine lines on her face and a healthy glow"
    return look
# looks replaced after the video model refused the first still (a likeness check); key -> look
LOOKX = {"mb-athletic": "short dark-brown hair with a slightly receding hairline, clean-shaven, an ordinary friendly everyday face with a broad nose, an original fictional person"}
def person(sex, age, goal):
    look = LOOKX.get(f"{sex}{age}-{goal}") or hair(sex, goal, age)
    return f"A {YEARS[age]}-year-old {PR[sex]['n']} with a {BUILD[sex][goal]}, {look}"
def pick(d, base, sex):
    return d.get(f"{base}_{sex}", d.get(base))
def g_still(key):
    sa, goal = key.split("-"); sex, age = sa[0], sa[1]
    return (f"{STYLE} {person(sex, age, goal)}, wearing {OUTFIT[sex][goal]}. Full body visible from head to toe, centered in the frame with a little headroom, "
            f"{pick(POSE, goal, sex)}. Straight-on full-body shot. Tasteful athletic styling. {NEG}")
def g_video(key):
    sa, goal = key.split("-"); sex = sa[0]; p = PR[sex]
    return (pick(MOVE, goal, sex).format(**p) + f" {p['His']} face, body size, clothing and the surroundings stay exactly as in the image. "
            "Locked-off camera, no camera movement, no cuts. No new objects, no text. The last frame matches the first frame so the clip loops seamlessly.")
def s_still(key):
    sa, goal, why = key.split("-"); sex = sa[0]; p = PR[sex]; d = SC[goal][why]
    scene = pick(d, "scene", sex).format(**p)
    return (f"Same {p['n']} as in the reference image (same face, same hair, same {BUILD[sex][goal].split(',')[0].split(' with')[0]}), {STYLE_REF}. "
            f"{p['He']} is wearing {d[sex]}. Scene: {scene} Medium-wide shot, {p['his']} whole body visible, {p['he']} is the clear focus of the image. {NEG}")
def s_video(key):
    sa, goal, why = key.split("-"); sex = sa[0]; p = PR[sex]; d = SC[goal][why]
    return (d["move"].format(**p) + f" {p['His']} face, hair, body and clothing stay consistent with the image. "
            "Smooth natural motion, gentle camera movement, no cuts, no new objects, no text.")

def load():
    """ids.txt is an event log. Lines:
      IDX JOB [STAMP]   a new job for IDX (clears its stamp and approval)
      S IDX STAMP       the job finished; STAMP is the YYYYMMDD_HHMMSS part of its result URL
      A IDX|IDX-IDX ... the current jobs of these indexes passed the visual check
      IDX -             forget the job of IDX (it will be made again)
    Returns (jobs, stamps, approved)."""
    J, S, A = {}, {}, set()
    f = os.path.join(HERE, "ids.txt")
    if not os.path.exists(f): return J, S, A
    for ln in open(f):
        t = ln.split()
        if len(t) < 2: continue
        if t[0] == "S" and len(t) >= 3: S[int(t[1])] = t[2]
        elif t[0] == "A":
            for x in t[1:]:
                a, _, b = x.partition("-")
                for i in range(int(a), int(b or a) + 1): A.add(i)
        elif t[0].isdigit():
            i = int(t[0]); S.pop(i, None); A.discard(i)
            if t[1] == "-": J.pop(i, None)
            else:
                J[i] = t[1]
                if len(t) >= 3: S[i] = t[2]
    return J, S, A
def ids():
    return load()[0]

IMG = dict(model="nano_banana_pro", resolution="2k", use_unlim=True)
VID = dict(model="seedance_2_5", mode="omni_reference", resolution="720p", duration=5, generate_audio=False, use_unlim=True)

def request(idx, J):
    G, S = gkeys(), skeys()
    if 1000 <= idx < 2000:
        return dict(index=idx, params=dict(IMG, aspect_ratio="3:4", prompt=g_still(G[idx - 1000])))
    if 2000 <= idx < 3000:
        key = S[idx - 2000]; ref = J.get(1000 + G.index(key.rsplit("-", 1)[0]))
        if not ref: return None
        return dict(index=idx, params=dict(IMG, aspect_ratio="4:3", medias=[dict(role="image_references", value=ref)], prompt=s_still(key)))
    if 3000 <= idx < 4000:
        ref = J.get(idx - 2000)
        if not ref: return None
        return dict(index=idx, params=dict(VID, aspect_ratio="3:4", medias=[dict(role="start_image", value=ref), dict(role="end_image", value=ref)], prompt=g_video(G[idx - 3000])))
    if 4000 <= idx < 5000:
        ref = J.get(idx - 2000)
        if not ref: return None
        return dict(index=idx, params=dict(VID, aspect_ratio="4:3", medias=[dict(role="start_image", value=ref)], prompt=s_video(S[idx - 4000])))
    raise SystemExit(f"bad index {idx}")

def write(name, idxs, J):
    reqs = [r for r in (request(i, J) for i in idxs) if r]
    os.makedirs(os.path.join(HERE, "plan"), exist_ok=True)
    json.dump(dict(requests=reqs), open(os.path.join(HERE, "plan", name + ".json"), "w"), ensure_ascii=False, indent=1)
    return len(reqs)

def main():
    J = ids(); G, S = gkeys(), skeys(); S_ = S; cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        os.makedirs(os.path.join(HERE, "plan"), exist_ok=True)
        json.dump(dict(g=G, s=S), open(os.path.join(HERE, "plan", "keys.json"), "w"), indent=0)
        rep = {}
        for kind, base, n in (("g_still", 1000, len(G)), ("s_still", 2000, len(S)), ("g_video", 3000, len(G)), ("s_video", 4000, len(S))):
            for b in range(0, n, 8):
                rep[f"{kind}_{b // 8:02d}"] = write(f"{kind}_{b // 8:02d}", range(base + b, base + min(b + 8, n)), J)
        print(json.dumps(rep))
    elif cmd == "batch":
        print(write(sys.argv[2], [int(x) for x in sys.argv[3:]], J))
    elif cmd == "todo":
        # python3 gen.py todo KIND [SIZE]: batches for every index of that kind without a job id yet -> plan/todo_KIND_NN.json
        kind = sys.argv[2]; size = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        base, n = dict(g_still=(1000, len(G)), s_still=(2000, len(S)), g_video=(3000, len(G)), s_video=(4000, len(S)))[kind]
        todo = [i for i in range(base, base + n) if i not in J and request(i, J)]
        for f in os.listdir(os.path.join(HERE, "plan")):
            if f.startswith(f"todo_{kind}_"): os.remove(os.path.join(HERE, "plan", f))
        out = []
        for b in range(0, len(todo), size):
            write(f"todo_{kind}_{b // size:02d}", todo[b:b + size], J); out.append(todo[b:b + size])
        print(json.dumps(out))
    elif cmd == "next":
        # python3 gen.py next N: the next N jobs to submit -> plan/next_vid.json and plan/next_img.json.
        # Videos first (all character loops, then end scenes whose still is finished and approved), stills fill the rest.
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        J, S, A = load()
        cv = [i for i in range(3000, 3000 + len(G)) if i not in J and (i - 2000) in S]
        cv += [i for i in range(4000, 4000 + len(S_)) if i not in J and (i - 2000) in A and (i - 2000) in S]
        ci = [i for i in range(2000, 2000 + len(S_)) if i not in J and request(i, J)]
        tv = cv[:n]; ti = ci[:max(0, n - len(tv))]
        write("next_vid", tv, J); write("next_img", ti, J)
        print(json.dumps(dict(vid=tv, img=ti, left=dict(vid=len(cv) - len(tv), img=len(ci) - len(ti)))))
    elif cmd == "status":
        J, S, A = load()
        def c(a, b): return [sum(1 for i in range(a, b) if i in J), sum(1 for i in range(a, b) if i in S)]
        print(json.dumps(dict(g_still=c(1000, 1030), s_still=c(2000, 2150) + [sum(1 for i in A if 2000 <= i < 2150)], g_video=c(3000, 3030), s_video=c(4000, 4150),
                              pending=sorted(i for i in J if i not in S))))
    elif cmd == "show":
        for x in sys.argv[2:]:
            r = request(int(x), J); print(x, json.dumps(r, ensure_ascii=False)[:1500] if r else "missing reference")
if __name__ == "__main__":
    main()
