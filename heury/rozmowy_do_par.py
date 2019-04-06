import json
import glob
import tqdm

def process_one(path):
    with open(path, 'r') as f:
        jj = json.loads(f.read())
    contents = [(x['sender_name'] == 'Bartosz Michalak', x['content']) for x in jj['messages'] if x['type'] == 'Generic' and 'content' in x]
    pyt_odp = []
    cur = True
    last = {True: '', False: ''}
    for x, y in contents[::-1]:
        last[x] = y
        if x != cur:
            pyt_odp.append((cur, (last[cur], last[x])))
            cur = x
    jaodp = [y for x, y in pyt_odp if not x]
    return jaodp

ret = []
alll = glob.glob('./**/*fixed.json')

for path in tqdm.tqdm(alll):
    ret.extend(process_one(path))

rozne = {}
for x, y in ret:
    x = x.lower()
    if x not in rozne:
        rozne[x] = []
    rozne[x].append(y)
# powtarzalne = { x: y for x, y in rozne.items() if len(x) < 15 }
powtarzalne = { x: y for x, y in rozne.items() if len(y) > 1 }
krotkie = { x: [z for z in y if len(z) < 20 or all(len(z) >= 20 for z in y)] for x, y in powtarzalne.items() }
for x, y in krotkie.items():
    print('{}: {}'.format(x, y))
