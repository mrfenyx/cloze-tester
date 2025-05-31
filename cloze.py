import re

def blank_word(word):
    length = len(word)
    if length <= 5:
        return word[0] + '-' * (length - 1) + f'({length})'
    else:
        return word[:2] + '-' * (length - 2) + f'({length})'

def blank_match(match):
    word = match.group(1)
    return blank_word(word)

def process_text(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    processed = []
    for s in sentences:
        s = re.sub(r'\[\[(\w+)\]\]', blank_match, s)
        processed.append(s)
    return processed
