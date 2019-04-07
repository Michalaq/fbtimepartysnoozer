#!/usr/bin/env python
from os import listdir
from os.path import join, isfile
from nltk import word_tokenize
from random import randrange
import pickle
import json

input_path = '../json/messages/inbox'
me = 'Jan Kopański'
global_msg_map = {}


def tokenize(text):
    return frozenset(word_tokenize(sanitize_content(text)))


def insert_map(msg_content, reply_content):
    if type(reply_content) is not list:
        reply_content = [reply_content]
    if msg_content in global_msg_map:
            global_msg_map[msg_content].extend(reply_content)
    else:
        global_msg_map[msg_content] = reply_content


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
        '.': None,
        ',': None,
        '\n': ' ',
        '\t': ' ',
        '\r': ' '
    }
    tab = {ord(k): v for k, v in tab.items()}
    return text.translate(tab).strip().lower()
    # return text.strip().lower()


def shingling_fill_map(messages):
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

    # if msg_groups[0][0]['sender_name'] == me:
    #     msg_groups = msg_groups[1:]

    i = 0
    if msg_groups[0][0]['sender_name'] == me:
        i = 1
    while i < len(msg_groups) - 1:
        # msg_content = sanitize_content(msg_groups[i][-1]['content'])
        # msg_tokens = set(word_tokenize(msg_content))
        assert msg_groups[i][-1]['content'] != me
        # do not remove this
        # msg_tokens = tokenize(msg_groups[i][-1]['content'])
        msg_tokens = set()
        for m in msg_groups[i]:
            for w in word_tokenize(sanitize_content(m['content'])):
                msg_tokens.add(w)
        msg_tokens = frozenset(msg_tokens)
        max_prop = 0
        reply_content = []
        for reply in msg_groups[i + 1]:
            assert reply['sender_name'] == me
            # reply_tokens = set(word_tokenize(sanitize_content(reply['content'])))
            reply_tokens = tokenize(reply['content'])
            intersection = msg_tokens & reply_tokens
            union = msg_tokens | reply_tokens
            prop = len(intersection) / len(union)
            if prop > max_prop:
                max_prop = prop
                reply_content = [reply['content']]
            elif prop == max_prop:
                reply_content.append(reply['content'])
        assert reply_content
        # insert_map(msg_content, reply_content)
        insert_map(msg_tokens, reply_content)
        i += 2


def naive_fill_map(messages):
    for i, msg in enumerate(messages[:-1]):
        if msg['sender_name'] != me and msg['type'] == 'Generic' and 'content' in msg:
            reply = messages[i + 1]
            if reply['sender_name'] == me and reply['type'] == 'Generic' and 'content' in reply:
                if len(reply['content']) < 30:
                    msg_content = tokenize(msg['content'])
                    if msg_content:
                        if msg_content in global_msg_map:
                            global_msg_map[msg_content].append(reply['content'])
                        else:
                            global_msg_map[msg_content] = [reply['content']]


def fill_map(messages):
    fun = lambda msg: msg['type'] == 'Generic' and 'content' in msg and msg['content']
    messages = list(filter(fun, messages))
    messages.reverse()
    naive_fill_map(messages)
    # shingling_fill_map(messages)


def fix_unicode(json):
    json['messages'] = [{k: v.encode('latin1').decode('utf8') if isinstance(v, str) else v for k, v in d.items()}
                        for d in json['messages']]


def build_map():
    for directory in listdir(input_path):
        json_path = join(input_path, directory, 'message_1.json')
        if isfile(json_path):
            with open(json_path) as json_file:
                json_data = json_file.read()
                jj = json.loads(json_data)
                fix_unicode(jj)
                # print(json['title'])
                fill_map(jj['messages'])


def generate_reply(msg_map, input_text):
    assert msg_map
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


class ShinglingMessenger:
    def __init__(self, model='map.p'):
        with open(model, 'rb') as pickle_file:
            self.msg_map = pickle.load(pickle_file)

    def query(self, query):
        return generate_reply(self.msg_map, query)


def test_main():
    sm = ShinglingMessenger()
    while True:
        input_text = input()
        reply_text = sm.query(input_text)
        print(reply_text)


def main():
    build_map()
    print('build complete')
    # with open('output.txt', 'w') as fout:
    #     for k, v in global_msg_map.items():
    #         fout.writelines(str((k, v)) + '\n')
    with open('map.p', 'wb') as map_file:
        pickle.dump(global_msg_map, map_file)
    print('save complete')
    while True:
        input_text = input()
        print(generate_reply(global_msg_map, input_text))


if __name__ == '__main__':
    main()
    # test_main()
