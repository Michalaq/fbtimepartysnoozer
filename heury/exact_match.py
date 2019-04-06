#!/usr/bin/env python
from os import listdir
from os.path import join, isfile
from json import loads
from nltk import word_tokenize
from random import randrange

input_path = '../json/messages/inbox'
me = 'Jan Kopański'
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


def sanitize_content(s):
    return s.strip().lower()


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
        msg_tokens = tokenize(msg_groups[i][-1]['content'])
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
                msg_content = tokenize(msg['content'])
                if msg_content in msg_map:
                    msg_map[msg_content].append(reply['content'])
                else:
                    msg_map[msg_content] = [reply['content']]


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
                json = loads(json_data)
                fix_unicode(json)
                # print(json['title'])
                fill_map(json['messages'])


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
