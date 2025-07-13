import openai

openai.api_key = 'your-api-key'

def get_saving_tip():
    prompt = "Give a short savings tip for someone who overspends monthly."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()


def predict_category(description):
    # Very basic keyword logic; replace later with AI or OpenAI API
    keywords = {
        "food": ["lunch", "dinner", "snack", "restaurant"],
        "travel": ["uber", "train", "bus", "flight"],
        "shopping": ["clothes", "shoes", "amazon"],
    }
    for category, words in keywords.items():
        if any(word in description.lower() for word in words):
            return category
    return "others"
