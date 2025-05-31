import re
from markupsafe import Markup

def blank_word(word, blank_id_start=0):
    # Only letters/numbers are counted for the prefix and blanks; punctuation/hyphens are always visible.
    alnum_chars = [c for c in word if c.isalnum()]
    length = len(alnum_chars)
    if length <= 5:
        num_reveal = 1
    elif length <= 7:
        num_reveal = 2
    elif length <= 9:
        num_reveal = 3
    else:
        num_reveal = 4

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
            # Always show hyphens/punctuation
            output += c
    output += '</span>'
    return Markup(output), blank_ids

def process_text_with_inputs(text):
    """
    Returns (cloze_html, blanks_info)
    - cloze_html: text with input fields (named blank_0, blank_1, ...)
    - blanks_info: list of dicts: {'name', 'word', 'prefix', 'num_inputs'}
    """
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
        if length <= 5:
            num_reveal = 1
        elif length <= 7:
            num_reveal = 2
        elif length <= 9:
            num_reveal = 3
        else:
            num_reveal = 4

        # Build prefix (letters/numbers), then add all following alnums as inputs, but copy hyphens/punct as-is
        prefix = ''
        current_letter = 0
        for c in word:
            if c.isalnum() and len(prefix) < num_reveal:
                prefix += c
                current_letter += 1

        # Count how many inputs (all alnums after the prefix)
        missing = length - len(prefix)
        # Create the input group HTML
        html_piece, next_id = blank_word(word, blank_id)
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
