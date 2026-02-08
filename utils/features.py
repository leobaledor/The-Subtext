# utils/features.py

import pandas as pd
from utils.tmdb_api import (
    get_director_or_writer_tmdb_id,
    get_directed_movies_from_tmdb
)

# =========================================================
# 1. Contar películas previas dirigidas por el director
# =========================================================
def count_previous_directed_movies(name, nomination_year, tmdb_key):
    """
    Cuenta cuántas películas dirigió el director ANTES del año de nominación.
    Requiere tmdb_key porque usa funciones de TMDb.
    """
    try:
        nomination_year = int(nomination_year)
    except:
        return None
    
    # 1. Obtener TMDb ID del director
    tmdb_id = get_director_or_writer_tmdb_id(name, tmdb_key)
    if tmdb_id is None:
        return None
    
    # 2. Obtener películas dirigidas
    movies = get_directed_movies_from_tmdb(tmdb_id, tmdb_key)
    if not movies:
        return 0
    
    # 3. Extraer años válidos
    years = []
    for m in movies:
        date = m.get("release_date")
        if date and len(date) >= 4:
            try:
                years.append(int(date[:4]))
            except:
                pass
    
    # 4. Contar películas anteriores al año de nominación
    previous = [y for y in years if y < nomination_year]
    
    return len(previous)


# =========================================================
# 2. Calcular edad del director al año de nominación
# =========================================================
def calculate_age_at_nomination(birthdate, nomination_year):
    if birthdate is None or pd.isna(birthdate):
        return None
    
    try:
        nomination_year = int(nomination_year)
    except:
        return None
    
    try:
        birth_year = int(birthdate.split("-")[0])
    except:
        return None
    
    return nomination_year - birth_year


# =========================================================
# 3. Contar número de compañías productoras
# =========================================================
def count_production_companies(companies):
    if isinstance(companies, list):
        return len(companies)
    return 0


# =========================================================
# 4. Determinar si la película es de un "big studio"
# =========================================================
BIG_STUDIOS = {
    "Warner Bros.",
    "Warner Bros. Pictures",
    "Universal Pictures",
    "Paramount Pictures",
    "Walt Disney Pictures",
    "20th Century Fox",
    "Columbia Pictures",
    "Sony Pictures",
    "Netflix",
    "Amazon Studios",
    "MGM",
    "New Line Cinema",
    "Lionsgate",
    "A24"
}

def is_big_studio(companies):
    if not isinstance(companies, list):
        return 0
    
    normalized = {c.strip() for c in companies}
    
    return 1 if normalized & BIG_STUDIOS else 0
