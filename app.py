# app.py

import streamlit as st
import pandas as pd

from utils.pipeline import run_full_pipeline

# ---------------------------------------------------------
# Título y descripción
# ---------------------------------------------------------
st.set_page_config(page_title="Predicción Oscar Mejor Película", page_icon="🎬")

st.title("🎬 Predicción de nominación al Oscar – Mejor Película")
st.write(
    "Ingresa el nombre de una película y el modelo estimará la probabilidad "
    "de que sea nominada al Oscar a Mejor Película."
)

# ---------------------------------------------------------
# Manejo de claves de API
# ---------------------------------------------------------
st.sidebar.header("Configuración de API keys")

# Opción 1: usar st.secrets (recomendado en Streamlit Cloud)
use_secrets = st.sidebar.checkbox(
    "Usar API keys desde `st.secrets`", value=True
)

if use_secrets:
    OMDB_API_KEY = st.secrets["OMDB_API_KEY"]
    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
else:
    OMDB_API_KEY = st.sidebar.text_input("OMDb API Key", type="password")
    TMDB_API_KEY = st.sidebar.text_input("TMDb API Key", type="password")

# Validación simple
if not OMDB_API_KEY or not TMDB_API_KEY:
    st.warning("Configura tus API keys de OMDb y TMDb en la barra lateral para poder hacer predicciones.")


# ---------------------------------------------------------
# Input principal: nombre de la película
# ---------------------------------------------------------
movie_name = st.text_input("Nombre de la película", placeholder="Ejemplo: Oppenheimer")

if st.button("Evaluar película"):
    if not movie_name.strip():
        st.error("Por favor ingresa un nombre de película válido.")
    elif not OMDB_API_KEY or not TMDB_API_KEY:
        st.error("Faltan las API keys de OMDb o TMDb.")
    else:
        with st.spinner("Buscando información y generando predicción..."):
            try:
                proba, poster_url, df_movie = run_full_pipeline(
                    movie_name,
                    omdb_key=OMDB_API_KEY,
                    tmdb_key=TMDB_API_KEY
                )
            except Exception as e:
                st.error(f"Ocurrió un error en el pipeline: {e}")
                st.stop()

        if proba is None or df_movie is None:
            st.error("No se pudo construir la información de la película. "
                     "Revisa el título o intenta con otra película.")
        else:
            # -------------------------------------------------
            # Resultado principal
            # -------------------------------------------------
            st.subheader("Resultado de la predicción")
            st.metric(
                label="Probabilidad de nominación a Mejor Película",
                value=f"{proba*100:.2f}%"
            )

            # -------------------------------------------------
            # Layout en columnas: póster + datos
            # -------------------------------------------------
            col1, col2 = st.columns([1, 2])

            with col1:
                if poster_url:
                    st.image(poster_url, caption=movie_name, use_column_width=True)
                else:
                    st.info("No se encontró póster para esta película.")

            with col2:
                st.markdown("**Datos principales de la película**")
                # Si df_movie tiene muchas columnas, mostramos solo algunas
                cols_to_show = [
                    c for c in df_movie.columns
                    if c in [
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
                        "is_award_season_release",
                        "is_big_studio",
                        "final_plot"
                    ]
                ]
                st.dataframe(df_movie[cols_to_show].T)

            # -------------------------------------------------
            # Sección opcional: ver todo el DataFrame
            # -------------------------------------------------
            with st.expander("Ver DataFrame completo usado por el modelo"):
                st.dataframe(df_movie)
