#!/usr/bin/env python
from os import listdir
from os.path import join, isfile
from json import loads
from nltk import word_tokenize
from random import randrange

input_path = ''
me = ''
msg_map = {}


def tokenize(text):
    return frozenset(word_tokenize(sanitize_content(text)))


def insert_map(msg_content, reply_content):
    if type(reply_content) is not list:
        reply_content = [reply_content]
    if msg_content in msg_map:
            msg_map[msg_content].extend(reply_content)
    else:
        msg_map[msg_content] = reply_content


def sanitize_content(text):
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
    }
    tab = {ord(k): v for k, v in tab.items()}
    return text.translate(tab).strip().lower()
    # return text.strip().lower()


def count_resemblance(q1, q2):
    intersection = q1 & q2
    union = q1 | q2
    prop = len(intersection) / len(union)
    return prop


def pair_queries(queries_replies):
    resemblance_threshold = 0.3
    queries_replies = [(k, v) for k, v in queries_replies.items()]
    for i, qra in enumerate(queries_replies):
        for qrb in queries_replies[i+1:]:
            resemblance = count_resemblance(qra[0], qrb[0])
            if resemblance > resemblance_threshold:
                print(qra[0], qrb[0])
                print(qra[1], qrb[1])


def filter_messages(messages):
    fun = lambda msg: msg['type'] == 'Generic' and 'content' in msg and msg['content']
    return list(filter(fun, messages))


def split_conversation(queries_replies, messages):
    if not messages:
        return
    msg_groups = []
    i = 0
    while i < len(messages):
        curr_sender = messages[i]['sender_name'] == me
        curr_group = [messages[i]]
        i += 1
        while i < len(messages) and curr_sender == (messages[i]['sender_name'] == me):
            curr_group.append(messages[i])
            i += 1
        msg_groups.append(curr_group)

    i = 0
    if msg_groups[0][0]['sender_name'] == me:
        i = 1
    while i < len(msg_groups) - 1:
        assert msg_groups[i][-1]['content'] != me
        msg_tokens = set()
        for m in msg_groups[i]:
            for w in word_tokenize(sanitize_content(m['content'])):
                msg_tokens.add(w)
        msg_tokens = frozenset(msg_tokens)
        # if msg_tokens:
        #     queries_replies.append((msg_tokens, list(map(lambda m: m['content'], msg_groups[i + 1]))))
            # queries_replies.append((msg_tokens, msg_groups[i + 1]))
        if msg_tokens not in queries_replies:
            queries_replies[msg_tokens] = []
        queries_replies[msg_tokens].extend(list(map(lambda m: m['content'], msg_groups[i + 1])))
        # queries_replies[msg_tokens].append(msg_groups[i + 1])
        i += 2
    return queries_replies


def fix_unicode(messages):
    return [{k: v.encode('latin1').decode('utf8') if isinstance(v, str) else v for k, v in d.items()} for d in messages]


def build_map():
    # queries_replies = []
    queries_replies = {}
    for directory in listdir(input_path):
        json_path = join(input_path, directory, 'message_1.json')
        if isfile(json_path):
            with open(json_path) as json_file:
                json_data = json_file.read()
                json = loads(json_data)
                messages = json['messages']
                messages = fix_unicode(messages)
                messages = filter_messages(messages)
                messages.reverse()
                split_conversation(queries_replies, messages)
    pair_queries(queries_replies)


def generate_reply(input_text):
    input_tokens = tokenize(input_text)
    max_prop = 0
    reply_content = []
    for k, v in msg_map.items():
        intersection = k & input_tokens
        union = k | input_tokens
        prop = len(intersection) / len(union)
        if prop > max_prop:
            max_prop = prop
            reply_content = v
        elif prop == max_prop:
            reply_content.extend(v)
    assert reply_content
    return reply_content[randrange(len(reply_content))]


def main():
    build_map()
    print('build complete')
    with open('output.txt', 'w') as fout:
        for k, v in msg_map.items():
            fout.writelines(str((k, v)) + '\n')
    print('save complete')
    while True:
        input_text = input()
        print(generate_reply(input_text))
    print('EOF')


if __name__ == '__main__':
    main()
