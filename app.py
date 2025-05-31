from flask import Flask, render_template, request
from cloze import process_text
from deepseek_api import generate_deepseek_text

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    input_text = ""
    error = ""
    subject = ""
    level = "B1"
    debug_log = []
    if request.method == "POST":
        debug_log.append("POST received. Entered POST handler.")
        subject = request.form.get("subject", "").strip()
        level = request.form.get("level", "B1").strip()
        input_text = request.form.get("input_text", "")
        debug_log.append(f"Subject: {subject}, Level: {level}")
        if request.form.get("generate"):
            debug_log.append("Form submit: GENERATE button pressed.")
            try:
                debug_log.append("Calling generate_deepseek_text (about to call)...")
                input_text = generate_deepseek_text(subject, level)
                debug_log.append("Returned from generate_deepseek_text (success).")
                debug_log.append("Received from DeepSeek:\n" + input_text)
                result = process_text(input_text)
                debug_log.append("Processed result:\n" + str(result))
            except Exception as e:
                error = f"DeepSeek API error: {str(e)}"
                debug_log.append("Exception: " + error)
        elif request.form.get("submit"):
            debug_log.append("Form submit: CLOZE button pressed.")
            result = process_text(input_text)
            debug_log.append("Processed result:\n" + str(result))
    else:
        debug_log.append("GET request.")
    # Print to server console for now
    print("\n--- Debug log ---")
    for log in debug_log:
        print(log)
    print("--- End Debug log ---\n")
    return render_template(
        "index.html",
        result=result,
        input_text=input_text,
        error=error,
        subject=subject,
        level=level,
        debug_log=debug_log,
    )

if __name__ == "__main__":
    app.run(debug=True)
