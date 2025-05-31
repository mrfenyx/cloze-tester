import yaml
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
api_key = config["deepseek"]["api_key"]
base_url = config["deepseek"]["base_url"]

client = OpenAI(api_key=api_key, base_url=base_url)

def generate_deepseek_text(subject, level):
    print("In generate_deepseek_text function...")  # Debug print
    prompt = (
        f"Generate a short text of 11-16 sentences about \"{subject}\" at CEFR level {level}.\n"
        f"INSTRUCTIONS FOR CLOZE EXERCISE:\n"
        f"1. In each sentence, select ONE content word (noun, verb, adjective, or adverb) to hide\n"
        f"2. The selected word must be 4 letters or longer\n"
        f"3. Wrap ONLY the selected word in double brackets, like this: [[word]]\n"
        f"4. Never mark proper nouns, articles, prepositions, or conjunctions\n"
        f"5. Ensure exactly one word is marked per sentence\n"
        f"6. Choose words that are important for understanding the sentence\n"
        f"\n"
        f"EXAMPLE:\n"
        f"The scientist conducted an [[experiment]] with careful precision.\n"
        f"Plants need [[sunlight]] to grow properly.\n"
        f"\n"
        f"Now generate the text about {subject} at level {level}, following all instructions precisely:"
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
