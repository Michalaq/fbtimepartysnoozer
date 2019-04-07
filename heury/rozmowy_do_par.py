import json
import glob
import tqdm
from trie import make_trie, search
import random

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
alll = glob.glob('../../../messages/inbox/**/*fixed.json')

for path in tqdm.tqdm(alll):
    ret.extend(process_one(path))

def sanitize(slowo):
    tab = {
        'ą': 'a',
        'ł': 'l',
        'ć': 'c',
        'ź': 'z',
        'ż': 'z',
        'ę': 'e',
        'ó': 'o',
        'ś': 's',
        'ń': 'n',
        '?': None,
        '!': None,
        '\n': ' ',
        '\t': ' ',
        '\r': ' '

    }
    tab = { ord(k): v for k, v in tab.items() }
    return slowo.lower().translate(tab).strip()

rozne = {}
for x, y in ret:
    x = sanitize(x)
    if x not in rozne:
        rozne[x] = []
    rozne[x].append(y)

# with open('ret.txt', 'w') as f:
#     f.write('\n'.join(
#         '\t'.join([x, y])
#         for x in rozne
#         for y in rozne[x]
#     ))

print('Making trie...')
trie = make_trie(rozne)
print('Done.')

trans = {
    'chuj': 'ch*j',
    'kurw': 'k*rw',
    'jeba': 'je*a',
    'jebi': 'je*i',
    'jebu': 'je*u',
    'jebo': 'je*o',
    'jeby': 'je*y',
    'cwel': '****',
    'cipa': 'ci*a',
    'pizd': 'piz*'
}

moje = [ x for y in rozne.values() for x in y ]

MAX_COST = 7
while True:
    try:
        query = input('> ')
        for i in range(MAX_COST):
            rets = search(trie, query, i)
            if rets:
                break
        if rets:
            ret = random.choice(random.choice(rets)[-1])
        else:
            ret = random.choice(moje)
        for x, y in trans.items():
            ret = ret.replace(x, y)
        print(ret)
    except KeyboardInterrupt:
        break
