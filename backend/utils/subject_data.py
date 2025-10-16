def get_predefined_answer(question):
    question = question.lower()

    if "newton" in question:
        return "Newton’s Second Law states that Force equals mass times acceleration (F = m × a)."

    elif "photosynthesis" in question:
        return "Photosynthesis is the process by which green plants use sunlight to make food from carbon dioxide and water."

    elif "python" in question and "variable" in question:
        return "In Python, a variable is a name that stores data value. Example: x = 10"

    elif "ai" in question or "artificial intelligence" in question:
        return "Artificial Intelligence is a field of computer science that enables machines to mimic human intelligence."

    else:
        return None
