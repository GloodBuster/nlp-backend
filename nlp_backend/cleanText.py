import re


def remove_duplicate_lines(text):
    lines = text.split("\n")
    # Trim whitespace and make lowercase
    lines = [line.strip().lower() for line in lines]
    lines = list(dict.fromkeys(lines))  # Removes duplicates
    return "\n".join(lines)


def clean_pdf_text(text):
    text = remove_duplicate_lines(text)
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub('[^a-zA-ZñÑáéíóúüÁÉÍÓÚÜ.,;¿?!¡]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text
