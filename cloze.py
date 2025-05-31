import re
from markupsafe import Markup

def get_num_reveal(length, reveal_rules):
    for rule in reveal_rules:
        if length <= rule['max_length']:
            return rule['num_reveal']
    return 1  # fallback

def blank_word(word, blank_id_start=0, reveal_rules=None):
    if reveal_rules is None:
        reveal_rules = [
            {"max_length": 5, "num_reveal": 1},
            {"max_length": 8, "num_reveal": 2},
            {"max_length": 11, "num_reveal": 3},
            {"max_length": 100, "num_reveal": 4}
        ]
    alnum_chars = [c for c in word if c.isalnum()]
    length = len(alnum_chars)
    num_reveal = get_num_reveal(length, reveal_rules)

    prefix_count = num_reveal
    current_letter = 0
    output = '<span class="cloze-blank-group">'
    blank_ids = blank_id_start
    for c in word:
        if c.isalnum():
            if current_letter < prefix_count:
                output += c
            else:
                output += (
                    f'<input type="text" name="blank_{blank_ids}" maxlength="1" class="blank-input" autocomplete="off">'
                )
                blank_ids += 1
            current_letter += 1
        else:
            output += c
    output += '</span>'
    return Markup(output), blank_ids

def process_text_with_inputs(text, reveal_rules=None):
    if reveal_rules is None:
        reveal_rules = [
            {"max_length": 5, "num_reveal": 1},
            {"max_length": 8, "num_reveal": 2},
            {"max_length": 11, "num_reveal": 3},
            {"max_length": 100, "num_reveal": 4}
        ]
    pattern = re.compile(r'\[\[([^\]]+)\]\]')
    output = ""
    last_end = 0
    blank_id = 0
    blanks_info = []
    for m in pattern.finditer(text):
        output += text[last_end:m.start()]
        word = m.group(1)
        alnum_chars = [c for c in word if c.isalnum()]
        length = len(alnum_chars)
        num_reveal = get_num_reveal(length, reveal_rules)

        # Build prefix (letters/numbers), then add all following alnums as inputs, but copy hyphens/punct as-is
        prefix = ''
        current_letter = 0
        for c in word:
            if c.isalnum() and len(prefix) < num_reveal:
                prefix += c
                current_letter += 1

        missing = length - len(prefix)
        html_piece, next_id = blank_word(word, blank_id, reveal_rules=reveal_rules)
        output += html_piece
        blanks_info.append({
            'name': f'blank_{blank_id}',
            'word': word,
            'prefix': prefix,
            'num_inputs': missing
        })
        blank_id = next_id
        last_end = m.end()
    output += text[last_end:]
    return Markup(output), blanks_info
