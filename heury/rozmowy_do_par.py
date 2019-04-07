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
# trie = None
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

def censor(slowo):
    for x, y in trans.items():
        slowo = slowo.replace(x, y)
    return slowo

moje = [ x for y in rozne.values() for x in y ]

rymy = {}
for x in moje:
    suf = x[-4:]
    if suf not in rymy:
        rymy[suf] = {}
    samocnt = sum(map(x.count, 'aeiouy'))
    if samocnt not in rymy[suf]:
        rymy[suf][samocnt] = []
    rymy[suf][samocnt].append(x)

MAX_COST = 7

def odpowiedz(query):
    for i in range(MAX_COST):
        rets = search(trie, query, i)
        if rets:
            break
    if rets:
        ret = random.choice(random.choice(rets)[-1])
    else:
        ret = random.choice(moje)
    ret = censor(ret)
    return ret

if __name__ == '__main__':
    mode = input('mode: ')
    while True:
        try:
            query = input('> ')
            if mode == 'chat':
                print(odpowiedz(query))
            elif mode == 'rap battle':
                qsuf = query[-4:]
                samocnt = sum(map(query.count, 'aeiouy'))
                if qsuf not in rymy:
                    print(censor(qsuf*(samocnt // 2)))
                    continue
                dists = {
                    (
                        abs(samocnt - x)
                    ): [y for y in rymy[qsuf][x] if sanitize(y.split(' ')[-1]) != sanitize(query.split(' ')[-1])] for x in rymy[qsuf] 
                }
                for i in range(100):
                    if i in dists and dists[i]:
                        print(censor(random.choice(dists[i])))
                        break
        except KeyboardInterrupt:
            break
