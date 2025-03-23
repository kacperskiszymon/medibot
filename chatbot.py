import openai, os
from faq import faq_data

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_bot_response(user_message):
    user_message_lower = user_message.lower()
    for question, answer in faq_data.items():
        if question in user_message_lower:
            return answer

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś pomocnym chatbotem gabinetu internistycznego MediBot."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content
