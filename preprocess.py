import re
import unicodedata
from bs4 import BeautifulSoup
import emoji

def preprocess_keywords(keywords):
    cleaned_keywords = []
    for kw in keywords:
        try:
            kw = kw.lower()
            kw = unicodedata.normalize("NFKC", kw)
            kw = BeautifulSoup(kw, "html.parser").get_text()
            kw = emoji.replace_emoji(kw, "")
            kw = re.sub(r"[^\w\s]", "", kw)
            words = kw.split()
            english_words = [w for w in words if re.match(r'^[a-z0-9]+$', w)]
            kw = " ".join(english_words)
            kw = re.sub(r"\s+", " ", kw).strip()
            if kw:
                cleaned_keywords.append(kw)
        except Exception:
            continue
    return cleaned_keywords
