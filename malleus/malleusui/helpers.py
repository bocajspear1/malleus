import re

def cleaned_username(username):
    return re.sub(r"[^_a-zA-Z0-9-]", "_", username)
