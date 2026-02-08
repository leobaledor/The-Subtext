# utils/text_processing.py
import nltk

# Asegurar que las stopwords estén disponibles en Streamlit Cloud
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")



import re
import pandas as pd
import emoji
from nltk.corpus import stopwords


# =========================================================
# 1. Limpieza de texto (tu función real)
# =========================================================
def clean_text(text):
    if pd.isna(text):
        return ""

    # remove emojis
    text = emoji.replace_emoji(text, replace='')

    # remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)

    # remove mentions/hashtags
    text = re.sub(r"[@#]\S+", "", text)

    # remove HTML
    text = re.sub(r"<.*?>", "", text)

    # normalize !!!! → !
    text = re.sub(r"([!?.,])\1+", r"\1", text)

    # normalize loooove → loove
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)

    # remove non-alphanumeric except typical punctuation
    text = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ.,!?'\s]", " ", text)

    # collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    # lowercase
    text = text.lower()

    # strip punctuation at ends
    text = text.strip(".,!?'-_()[]{};:\"")

    return text


# =========================================================
# 2. Stopwords (tu código real)
# =========================================================
# Nota: se recomienda ejecutar en tu entorno:
#   import nltk
#   nltk.download("stopwords")
stop_words = [clean_text(x) for x in stopwords.words("english")]
