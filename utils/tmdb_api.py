# utils/tmdb_api.py

import requests
import pandas as pd


# =========================================================
# 1. Obtener información básica de la película (OMDb + TMDb)
# =========================================================
def get_basic_movie_info_df(title, omdb_key, tmdb_key):
    # 1) Buscar en OMDb
    omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={omdb_key}"
    omdb_data = requests.get(omdb_url).json()

    if omdb_data.get("Response") == "False":
        return pd.DataFrame([{
            "title": None,
            "year": None,
            "imdb_id": None,
            "tmdb_id": None,
            "error": "No se encontró la película en OMDb"
        }])

    imdb_id = omdb_data.get("imdbID")
    year = omdb_data.get("Year")
    official_title = omdb_data.get("Title")

    # 2) Buscar en TMDb
    tmdb_search_url = (
        f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_key}&query={title}"
    )
    tmdb_search = requests.get(tmdb_search_url).json()

    if len(tmdb_search.get("results", [])) == 0:
        tmdb_id = None
    else:
        tmdb_id = tmdb_search["results"][0]["id"]

    # 3) Convertir a DataFrame
    df = pd.DataFrame([{
        "title": official_title,
        "year": year,
        "imdb_id": imdb_id,
        "tmdb_id": tmdb_id
    }])

    return df


# =========================================================
# 2. Obtener rating y el director de OMDb
# =========================================================
def get_movie_info(imdb_id, omdb_key):
    if pd.isna(imdb_id):
        return pd.Series([None, None])
    
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": omdb_key,
        "i": imdb_id
    }
    
    r = requests.get(url, params=params)
    data = r.json()
    
    rating = float(data.get("imdbRating")) if data.get("imdbRating") not in [None, "N/A"] else None
    director = data.get("Director")
    
    return pd.Series([rating, director])


# =========================================================
# 3. Obtener runtime, genre, plot desde OMDb
# =========================================================
def get_omdb_details(imdb_id, omdb_key):
    if pd.isna(imdb_id):
        return pd.Series([None, None, None])
    
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": omdb_key,
        "i": imdb_id
    }
    
    r = requests.get(url, params=params).json()

    # 1. Duración (runtime)
    runtime_str = r.get("Runtime")
    runtime = None

    if runtime_str and runtime_str != "N/A":
        try:
            if "min" in runtime_str and "h" not in runtime_str:
                runtime = int(runtime_str.replace(" min", "").strip())
            elif "h" in runtime_str:
                partes = (
                    runtime_str.lower()
                    .replace("min", "")
                    .replace("  ", " ")
                    .split()
                )
                horas = 0
                minutos = 0

                if "h" in partes:
                    h_index = partes.index("h")
                    horas = int(partes[h_index - 1])

                if "h" in partes and len(partes) > partes.index("h") + 1:
                    minutos = int(partes[partes.index("h") + 1])

                runtime = horas * 60 + minutos

        except:
            runtime = None

    # 2. Género
    genre = r.get("Genre")
    if genre in [None, "N/A"]:
        genre = None

    # 3. Sinopsis
    plot = r.get("Plot")
    if plot in [None, "N/A"]:
        plot = None

    return pd.Series([runtime, genre, plot])


# =========================================================
# 4. Obtener TMDb ID del director / escritor / actor / etc.
# =========================================================
def get_director_or_writer_tmdb_id(name, tmdb_key):
    url = "https://api.themoviedb.org/3/search/person"
    params = {
        "api_key": tmdb_key,
        "query": name
    }
    
    try:
        r = requests.get(url, params=params, timeout=10).json()
    except:
        return None
    
    results = r.get("results", [])
    if not results:
        return None
    
    # 1) DIRECTORES
    directors = [
        person for person in results
        if person.get("known_for_department") == "Directing"
    ]
    if directors:
        return directors[0]["id"]
    
    # 2) ESCRITORES
    writers = [
        person for person in results
        if person.get("known_for_department") == "Writing"
    ]
    if writers:
        return writers[0]["id"]
    
    # 3) ACTORES
    actors = [
        person for person in results
        if person.get("known_for_department") == "Acting"
    ]
    if actors:
        return actors[0]["id"]
    
    # 4) PRODUCTORES
    producers = [
        person for person in results
        if person.get("known_for_department") == "Production"
    ]
    if producers:
        return producers[0]["id"]
    
    # 5) CAMARÓGRAFOS / CINEMATÓGRAFOS
    cinematographers = [
        person for person in results
        if person.get("known_for_department") in ["Camera", "Cinematography"]
    ]
    if cinematographers:
        return cinematographers[0]["id"]
    
    return None


# =========================================================
# 5. Obtener rating previo del director
# =========================================================
def get_previous_director_imdb_rating(
    director_tmdb_id,
    current_imdb_id,
    nomination_year,
    imdb_rating_actual,
    omdb_key,
    tmdb_key
):
    try:
        nomination_year = int(nomination_year)
    except:
        return imdb_rating_actual
    
    url = f"https://api.themoviedb.org/3/person/{director_tmdb_id}/movie_credits?api_key={tmdb_key}"
    data = requests.get(url).json()
    
    if "crew" not in data:
        return imdb_rating_actual
    
    directed_movies = [m for m in data["crew"] if m.get("job") == "Director"]
    if not directed_movies:
        return imdb_rating_actual
    
    movies = []
    for m in directed_movies:
        release_date = m.get("release_date")
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
                movies.append({"tmdb_id": m["id"], "year": year})
            except:
                continue
    
    if not movies:
        return imdb_rating_actual
    
    movies = sorted(movies, key=lambda x: x["year"])
    
    lookup_url = (
        f"https://api.themoviedb.org/3/find/{current_imdb_id}"
        f"?api_key={tmdb_key}&external_source=imdb_id"
    )
    lookup = requests.get(lookup_url).json()
    
    if "movie_results" not in lookup or len(lookup["movie_results"]) == 0:
        return imdb_rating_actual
    
    current_tmdb_id = lookup["movie_results"][0]["id"]
    
    idx = None
    for i, m in enumerate(movies):
        if m["tmdb_id"] == current_tmdb_id:
            idx = i
            break
    
    if idx is None:
        return imdb_rating_actual
    
    if idx == 0:
        return imdb_rating_actual
    
    prev_tmdb_id = movies[idx - 1]["tmdb_id"]
    
    prev_lookup_url = (
        f"https://api.themoviedb.org/3/movie/{prev_tmdb_id}/external_ids?api_key={tmdb_key}"
    )
    prev_lookup = requests.get(prev_lookup_url).json()
    
    prev_imdb_id = prev_lookup.get("imdb_id")
    if not prev_imdb_id:
        return imdb_rating_actual
    
    omdb_url = f"http://www.omdbapi.com/?i={prev_imdb_id}&apikey={omdb_key}"
    omdb_data = requests.get(omdb_url).json()
    
    if omdb_data.get("Response") == "False":
        return imdb_rating_actual
    
    rating = omdb_data.get("imdbRating")
    
    try:
        return float(rating)
    except:
        return imdb_rating_actual


# =========================================================
# 6. Obtener detalles TMDb: budget, revenue, popularity, production_companies
# =========================================================
def get_tmdb_movie_details(tmdb_id, tmdb_key):
    if pd.isna(tmdb_id):
        return pd.Series([None, None, None, None])
    
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": tmdb_key, "language": "en-US"}
    
    r = requests.get(url, params=params).json()
    
    budget = r.get("budget")
    revenue = r.get("revenue")
    popularity = r.get("popularity")
    
    companies = r.get("production_companies", [])
    company_names = [c["name"] for c in companies]
    
    return pd.Series([budget, revenue, popularity, company_names])


# =========================================================
# 7. Obtener el número de películas dirigidas por el director
# =========================================================
def get_directed_movies_from_tmdb(person_id, tmdb_key):
    url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"
    params = {"api_key": tmdb_key}

    try:
        r = requests.get(url, params=params, timeout=10).json()
    except:
        return []

    crew = r.get("crew", [])
    directed = [m for m in crew if m.get("job") == "Director"]
    return directed


# =========================================================
# 8. Obtener fecha de nacimiento del director
# =========================================================
def get_birthdate_from_tmdb(tmdb_id, tmdb_key):
    if pd.isna(tmdb_id):
        return None
    
    url = f"https://api.themoviedb.org/3/person/{tmdb_id}"
    params = {"api_key": tmdb_key}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return None
        
        data = r.json()
        return data.get("birthday")
    
    except:
        return None


# =========================================================
# 9. Obtener mes de estreno
# =========================================================
def get_release_month_tmdb(tmdb_id, tmdb_key):
    if tmdb_id is None:
        return None
    
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": tmdb_key}
    
    r = requests.get(url, params=params).json()
    date_str = r.get("release_date")
    
    if not date_str:
        return None
    
    try:
        return int(date_str.split("-")[1])
    except:
        return None


# =========================================================
# 10. Obtener poster
# =========================================================
def get_movie_poster_url(tmdb_id, tmdb_key):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={tmdb_key}"
    data = requests.get(url).json()
    poster_path = data.get("poster_path")
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None
