import re

def clean_text(text):
    """
    Removes unwanted characters and spaces.
    """
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s?.!,]', '', text)
    return text
