import re


def is_url(text):
    return text.startswith("http://") or text.startswith("https://")


def smart_query_mode(query, platform):
    if is_url(query):
        return query
    return f"{'ytsearch' if platform == 'YouTube' else 'scsearch'}:{query}"


def preprocess_queries(raw_text, remove_number=True):
    lines = raw_text.splitlines()
    cleaned = []
    for line in lines:
        if remove_number:
            line = re.sub(r"^\s*\d+[\.\-\s]+", "", line)
        if line.strip():
            cleaned.append(line.strip())
    return cleaned
