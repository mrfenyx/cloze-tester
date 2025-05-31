import yaml
from openai import OpenAI

print("deepseek_api.py loaded!")  # Add this at top for sanity check

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
DEEPSEEK_API_KEY = config["deepseek"]["api_key"]
DEEPSEEK_BASE_URL = config["deepseek"]["base_url"]

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

def generate_deepseek_text(subject, level):
    print("In generate_deepseek_text function...")  # Debug print
    prompt = (
        f"You are an English language exercise generator."
        f"Write a short text of 11-16 sentences about \"{subject}\" at CEFR level {level}.\n"
        f"In each sentence, mark ONE word to be hidden by wrapping it in double brackets. Example: The car uses [[batteries]] for power."
        f"Do not replace the word, just mark it. Do not mark words shorter than 4 letters. Choose important words (nouns, verbs, adjectives)."
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful English language exercise generator."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )
        print("DeepSeek API returned a response!")
        return response.choices[0].message.content
    except Exception as e:
        print("Error in generate_deepseek_text:", e)
        raise
