# model.py
from utils.subject_data import get_predefined_answer

# Optionally import a model (if using offline AI)
from transformers import pipeline
bot = pipeline("text-generation", model="distilgpt2")

def get_answer(prompt):
    """
    Generate AI-based or predefined answers.
    """
    # Step 1: Check if the question matches a known subject answer
    predefined = get_predefined_answer(prompt)
    if predefined:
        return predefined

    # Step 2: Else, use AI model to generate a reply
    reply = bot(prompt, max_length=60, num_return_sequences=1)
    return reply[0]['generated_text']
