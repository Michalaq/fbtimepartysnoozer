import json
import sys
import os
import glob

def fix(path):
    with open(path, 'r') as f:
        with open(path.replace('.json', '_fixed.json'), 'w+') as out:
            data = f.read()
            j = json.loads(data)
            j['messages'] = [{k: v.encode('latin1').decode('utf8') if isinstance(v, str) else v for k, v in d.items()} for d in j['messages']]
    
            json.dump(j, out, indent=4, ensure_ascii=False)

for p in glob.glob('./**/message_1.json'):
    print(p)
    fix(p)
