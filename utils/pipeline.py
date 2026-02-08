# utils/pipeline.py

import joblib
from utils.build_dataframe import build_movie_dataframe
from utils.preprocess import preprocess_movie_df
from utils.tmdb_api import get_movie_poster_url


# =========================================================
# Cargar modelo, tokenizer y embeddings
# =========================================================
def load_artifacts():
    """
    Carga todos los artefactos necesarios:
    - modelo entrenado
    - tokenizer
    - embedding_index
    """
    model = joblib.load("modelo_prediccion_nominacion_oscar_v2.pkl")
    tokenizer = joblib.load("tokenizer_modelo_prediccion_nominacion_oscar_v2.pkl")
    embedding_index = joblib.load("glove_index_modelo_prediccion_nominacion_oscar_v2.pkl")

    return model, tokenizer, embedding_index


# =========================================================
# Pipeline maestro
# =========================================================
def run_full_pipeline(movie_name, omdb_key, tmdb_key):
    """
    Ejecuta TODO el flujo:
    1. Construir dataframe con todas las features
    2. Preprocesar columnas en el orden correcto
    3. Predecir probabilidad con el modelo
    4. Obtener poster desde TMDb
    """

    # 1. Cargar artefactos
    model, tokenizer, embedding_index = load_artifacts()

    # 2. Construir DataFrame completo
    df_movie = build_movie_dataframe(
        title=movie_name,
        tokenizer=tokenizer,
        embedding_index=embedding_index,
        omdb_key=omdb_key,
        tmdb_key=tmdb_key
    )

    if df_movie is None:
        return None, None, None

    # 3. Preprocesar columnas
    X = preprocess_movie_df(df_movie)

    # 4. Predecir probabilidad
    proba = model.predict_proba(X)[0][1]

    # 5. Obtener poster
    poster_url = None
    if "tmdb_id" in df_movie.columns:
        tmdb_id = df_movie["tmdb_id"].iloc[0]
        if tmdb_id is not None:
            poster_url = get_movie_poster_url(tmdb_id, tmdb_key)


    return proba, poster_url, df_movie
