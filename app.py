import logging
import json
import re
from flask import Flask, render_template, request
from deepseek_api import generate_deepseek_text
from cloze import process_text_with_inputs
from markupsafe import Markup

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    cloze_html = ""
    blanks_info = []
    subject = ""
    level = "B1"
    error = ""
    generated_text = ""
    feedback_html = ""
    score_str = ""

    if request.method == "POST":
        if "generate" in request.form:
            # Generate cloze
            subject = request.form.get("subject", "")
            level = request.form.get("level", "B1")
            try:
                generated_text = generate_deepseek_text(subject, level)
                cloze_html, blanks_info = process_text_with_inputs(generated_text)
            except Exception as e:
                error = str(e)
        elif "check" in request.form:
            # Check answers (using flat_idx for all blanks, including hyphens/punct)
            generated_text = request.form.get("generated_text", "")
            blanks_info = json.loads(request.form.get("blanks_info", "[]"))
            total = len(blanks_info)
            correct = 0
            blank_pattern = re.compile(r'\[\[([^\]]+)\]\]')
            blank_id = 0
            flat_idx = 0  # Flat input counter across all words

            def repl(m):
                nonlocal blank_id, correct, flat_idx
                info = blanks_info[blank_id]
                word = info['word']
                prefix = info['prefix']
                n_inputs = info['num_inputs']
                user_input = ''
                input_fields = ''
                is_correct = True
                for i in range(n_inputs):
                    val = request.form.get(f'blank_{flat_idx}', '')
                    user_input += val
                    # Compare each letter to the correct answer for is_correct (per word)
                    if len(word[len(prefix):]) > i:
                        if val.lower() != word[len(prefix):][i].lower():
                            is_correct = False
                    else:
                        is_correct = False
                    input_fields += f'<input type="text" value="{val}" maxlength="1" readonly class="blank-input{" correct" if is_correct else " incorrect"}">'
                    flat_idx += 1
                if is_correct and user_input.lower() == word[len(prefix):].lower():
                    correct += 1
                    html = f'<span class="cloze-blank-group correct">{prefix}{input_fields}</span>'
                else:
                    html = f'<span class="cloze-blank-group incorrect">{prefix}{input_fields}</span> <span class="correct-answer">({word})</span>'
                blank_id += 1
                return html

            feedback_html = Markup(blank_pattern.sub(repl, generated_text))
            score_str = f"{correct}/{total} correct"

    return render_template(
        "index.html",
        subject=subject,
        level=level,
        cloze_html=cloze_html,
        feedback_html=feedback_html,
        error=error,
        generated_text=generated_text,
        blanks_info=json.dumps(blanks_info),
        score_str=score_str
    )

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(debug=True)
