# utils/preprocess.py

import pandas as pd

# =========================================================
# Columnas numéricas usadas por tu modelo
# =========================================================
NUM_COLS = [
    "imdb_rating",
    "imdb_rating_prev",
    "runtime",
    "popularity",
    "director_previous_movies",
    "director_age_at_nomination",
    "release_month",
    "ratio_utility",
    "num_genres",
    "num_production_companies",
]

# =========================================================
# Columnas categóricas (ya son 0/1 en tu pipeline)
# =========================================================
CAT_COLS = [
    "is_award_season_release",
    "is_big_studio"
]

# =========================================================
# Columnas de embeddings GloVe (100 dimensiones)
# =========================================================
EMB_COLS = [f"emb_{i}" for i in range(100)]


# =========================================================
# Función principal de preprocesamiento
# =========================================================
def preprocess_movie_df(df):
    """
    Ordena las columnas del DataFrame en el orden exacto
    que el modelo espera.
    No hace escalado ni one-hot porque tu modelo ya fue
    entrenado con los valores tal cual.
    """

    ordered_cols = NUM_COLS + CAT_COLS + EMB_COLS

    # Validación opcional (útil para debugging)
    missing = [c for c in ordered_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el DataFrame: {missing}")

    return df[ordered_cols]
