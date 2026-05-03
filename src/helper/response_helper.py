import re
import json


def safe_json(text):
    if not isinstance(text, str):
        return text

    text = text.strip()

    # extract object or array
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not match:
        return None

    return json.loads(match.group(1))