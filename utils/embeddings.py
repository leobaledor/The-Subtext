# utils/embeddings.py

import numpy as np


# =========================================================
# 1. Convertir texto → embedding promedio GloVe
#    (tu función real, organizada y lista para producción)
# =========================================================
def plot_to_embedding(
    text,
    tokenizer,
    embedding_index,
    max_nb_words=3000,
    embedding_dim=50
):
    """
    Convierte un texto limpio en un vector de embedding
    usando el tokenizer entrenado y el diccionario GloVe cargado.

    - text: string ya limpiado
    - tokenizer: tokenizer entrenado (joblib.load)
    - embedding_index: diccionario {palabra: vector}
    - max_nb_words: tamaño máximo del vocabulario
    - embedding_dim: dimensión del vector GloVe (50, 100, 200, 300)
    """

    if not isinstance(text, str):
        return np.zeros(embedding_dim)

    # Convertir texto a secuencia de índices
    seq = tokenizer.texts_to_sequences([text])[0]
    vectors = []

    # Convertir cada índice → palabra → vector GloVe
    for idx in seq:
        if idx < max_nb_words:
            word = tokenizer.index_word.get(idx)
            if word in embedding_index:
                vectors.append(embedding_index[word])

    # Si no hay palabras válidas → vector de ceros
    if len(vectors) == 0:
        return np.zeros(embedding_dim)

    # Promedio de embeddings
    return np.mean(vectors, axis=0)
