import re

def clean_text(text):
    """
    Remove HTML tags and special characters from text.
    """
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[\r\n]+', ' ', text)  # Replace line breaks with space
    text = re.sub(r'[^\w\s.,!?\'"]', '', text)  # Remove special characters except common punctuations
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def preprocess_data(data):
    """
    Preprocess a dictionary of data by cleaning its text fields.
    """
    if 'title' in data:
        data['title'] = clean_text(data['title'])
    if 'content' in data:
        data['content'] = clean_text(data['content'])
    return data
