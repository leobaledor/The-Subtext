# utils/build_dataframe.py

import pandas as pd

from utils.tmdb_api import (
    get_basic_movie_info_df,
    get_movie_info,
    get_omdb_details,
    get_director_or_writer_tmdb_id,
    get_previous_director_imdb_rating,
    get_tmdb_movie_details,
    get_directed_movies_from_tmdb,
    get_birthdate_from_tmdb,
    get_release_month_tmdb
)

from utils.features import (
    count_previous_directed_movies,
    calculate_age_at_nomination,
    count_production_companies,
    is_big_studio
)

from utils.text_processing import clean_text, stop_words
from utils.embeddings import plot_to_embedding


def build_movie_dataframe(
    title,
    tokenizer,
    embedding_index,
    omdb_key,
    tmdb_key
):
    """
    Construye el DataFrame final con TODAS las features necesarias
    para alimentar el modelo.
    """

    # 1. Información básica
    df = get_basic_movie_info_df(title, omdb_key, tmdb_key)

    if df is None or df.empty or df["imdb_id"].iloc[0] is None:
        return None

    df["year"] = df["year"].astype(float)

    # 2. imdb_rating y director
    df[["imdb_rating", "director"]] = df["imdb_id"].apply(
        lambda imdb: get_movie_info(imdb, omdb_key)
    )

    df["director_first"] = df["director"].apply(lambda x: x.split(",")[0].strip())

    # 3. runtime, genre, plot
    df[["runtime", "genre", "plot"]] = df["imdb_id"].apply(
        lambda imdb: get_omdb_details(imdb, omdb_key)
    )

    # 4. TMDb ID del director
    df["director_tmdb_id"] = df["director_first"].apply(
        lambda name: get_director_or_writer_tmdb_id(name, tmdb_key)
    )

    # 5. IMDb rating previo del director
    df["imdb_rating_prev"] = df.apply(
        lambda row: get_previous_director_imdb_rating(
            director_tmdb_id=row["director_tmdb_id"],
            current_imdb_id=row["imdb_id"],
            nomination_year=row["year"],
            imdb_rating_actual=row["imdb_rating"],
            omdb_key=omdb_key,
            tmdb_key=tmdb_key
        ),
        axis=1
    )

    # 6. budget, revenue, popularity, production_companies
    df[["budget", "revenue", "popularity", "production_companies"]] = \
        df["tmdb_id"].apply(lambda tmdb_id: get_tmdb_movie_details(tmdb_id, tmdb_key))

    # 7. Número de películas previas del director
    df["director_previous_movies"] = df.apply(
        lambda row: count_previous_directed_movies(
            row["director_first"],
            row["year"],
            tmdb_key
        ),
        axis=1
    )

    # 8. Fecha de nacimiento del director
    df["director_birthdate"] = df["director_tmdb_id"].apply(
        lambda tmdb_id: get_birthdate_from_tmdb(tmdb_id, tmdb_key)
    )

    # 9. Edad del director
    df["director_age_at_nomination"] = df.apply(
        lambda row: calculate_age_at_nomination(row["director_birthdate"], row["year"]),
        axis=1
    )

    # 10. Mes de estreno
    df["release_month"] = df["tmdb_id"].apply(
        lambda tmdb_id: get_release_month_tmdb(tmdb_id, tmdb_key)
    )

    df["is_award_season_release"] = df["release_month"].apply(
        lambda m: 1 if m in [10, 11, 12] else 0
    )

    # 11. Limpieza de plot
    df["cleaned_plot"] = df["plot"].apply(clean_text)
    df["final_plot"] = df["cleaned_plot"].map(
        lambda s: " ".join([w for w in s.split() if w not in stop_words])
    )

    # 12. Productoras
    df["num_production_companies"] = df["production_companies"].apply(count_production_companies)
    df["is_big_studio"] = df["production_companies"].apply(is_big_studio)

    # 13. Número de géneros
    df["num_genres"] = df["genre"].str.split(",").apply(len)

    # 14. ratio_utility
    df["ratio_utility"] = df["revenue"] / df["budget"]

    # 15. Selección de columnas finales
    cols = [
        "tmdb_id",
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

    df = df[cols].copy()

    # 16. Embeddings GloVe
    df["embedding"] = df["final_plot"].apply(
        lambda x: plot_to_embedding(x, tokenizer, embedding_index)
    )

    emb_df = pd.DataFrame(df["embedding"].tolist(),
                          columns=[f"emb_{i}" for i in range(100)])

    df = pd.concat([df, emb_df], axis=1)
    df = df.drop(columns=["embedding"])

    return df
