import re
from markupsafe import Markup

def blank_word(word, blank_id_start=0):
    length = len(word)
    # Adaptive prefix reveal
    if length <= 5:
        num_reveal = 1
    elif length <= 7:
        num_reveal = 2
    elif length <= 9:
        num_reveal = 3
    else:
        num_reveal = 4

    prefix = word[:num_reveal]
    missing = length - num_reveal
    start_inputs = blank_id_start
    inputs = ''.join([
        f'<input type="text" name="blank_{start_inputs+i}" maxlength="1" class="blank-input" autocomplete="off">'
        for i in range(missing)
    ])
    return Markup(f'<span class="cloze-blank-group">{prefix}{inputs}</span>'), blank_id_start + missing

def blank_match(match, blank_id_start):
    word = match.group(1)
    return blank_word(word, blank_id_start)

def process_text_with_inputs(text):
    """
    Process the text and replace each [[word]] with a prefix and <input> fields for each missing character.
    Returns the HTML string.
    """
    pattern = re.compile(r'\[\[(\w+)\]\]')
    output = ""
    last_end = 0
    blank_id = 0
    for m in pattern.finditer(text):
        output += text[last_end:m.start()]
        html_piece, next_id = blank_word(m.group(1), blank_id)
        output += html_piece
        blank_id = next_id
        last_end = m.end()
    output += text[last_end:]
    return Markup(output)
