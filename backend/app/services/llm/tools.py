import requests


API_BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# CONFIGURATION
# =========================================================

MAX_STATION_CANDIDATES = 3


# =========================================================
# NORMALISATION AQST
# =========================================================

def normalize_aqst_station(name: str) -> str:
    """
    Convertit certains noms de gares GTFS vers
    les noms utilisés par les données AQST.

    Cette normalisation reste volontairement simple
    pour le MVP.
    """

    normalized = name.strip().upper()

    mapping = {
        "PARIS GARE DE LYON HALL 1 - 2": "PARIS LYON",
        "PARIS GARE DE LYON": "PARIS LYON",
        "LYON PART DIEU": "LYON PART DIEU",
    }

    return mapping.get(
        normalized,
        normalized,
    )


# =========================================================
# TOOL 1 — PREDICTION DE RETARD
# =========================================================

def predict_delay(
    annee: int,
    mois: int,
    gare_depart: str,
    gare_arrivee: str,
):
    """
    Prédit le retard moyen d'une liaison ferroviaire.

    Pour ce tool, les gares doivent être suffisamment
    précises avant l'appel.

    Exemple :
        Paris Gare de Lyon -> Lyon Part Dieu
    """

    gare_depart = normalize_aqst_station(
        gare_depart
    )

    gare_arrivee = normalize_aqst_station(
        gare_arrivee
    )

    response = requests.post(
        f"{API_BASE_URL}/predictions/delay/route",
        json={
            "annee": annee,
            "mois": mois,
            "gare_depart": gare_depart,
            "gare_arrivee": gare_arrivee,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# RÉSOLUTION DES GARES
# =========================================================

def resolve_stations(query: str):
    """
    Retourne plusieurs gares candidates correspondant
    à une ville ou à un nom de gare.

    Exemple :

        Paris

        peut retourner :

        Paris Gare de Lyon
        Paris Montparnasse
        Paris Nord
        etc.
    """

    response = requests.get(
        f"{API_BASE_URL}/stations/search",
        params={
            "q": query,
        },
        timeout=10,
    )

    response.raise_for_status()

    stations = response.json()

    if not stations:
        raise ValueError(
            f"Aucune gare trouvée pour : {query}"
        )

    return stations


# =========================================================
# TOOL 2 — RECHERCHE DE TRAJETS
# =========================================================

def search_trips(
    departure: str,
    arrival: str,
    travel_date: str,
    departure_after: str,
):
    """
    Recherche des trajets entre deux villes
    ou deux gares.

    Si l'utilisateur fournit simplement une ville,
    plusieurs gares candidates sont testées.

    Exemple :

        Paris -> Lyon

    peut permettre de trouver :

        Paris Gare de Lyon -> Lyon Part Dieu
    """

    # -----------------------------------------------------
    # Résolution des gares
    # -----------------------------------------------------

    departure_candidates = resolve_stations(
        departure
    )[:MAX_STATION_CANDIDATES]

    arrival_candidates = resolve_stations(
        arrival
    )[:MAX_STATION_CANDIDATES]

    print(
        "Gares de départ testées :",
        [
            station["name"]
            for station in departure_candidates
        ],
    )

    print(
        "Gares d'arrivée testées :",
        [
            station["name"]
            for station in arrival_candidates
        ],
    )

    all_trips = []

    # -----------------------------------------------------
    # Test des différentes combinaisons de gares
    # -----------------------------------------------------

    for departure_station in departure_candidates:

        for arrival_station in arrival_candidates:

            response = requests.get(
                f"{API_BASE_URL}/trips/search",
                params={
                    "departure": departure_station[
                        "external_id"
                    ],
                    "arrival": arrival_station[
                        "external_id"
                    ],
                    "travel_date": travel_date,
                    "departure_after": departure_after,
                },
                timeout=10,
            )

            response.raise_for_status()

            trips = response.json()

            if not trips:
                continue

            # -------------------------------------------------
            # Conservation des gares résolues
            # -------------------------------------------------

            for trip in trips:

                trip[
                    "resolved_departure_station"
                ] = departure_station["name"]

                trip[
                    "resolved_arrival_station"
                ] = arrival_station["name"]

                all_trips.append(
                    trip
                )

    # -----------------------------------------------------
    # Suppression des doublons
    # -----------------------------------------------------

    unique_trips = {}

    for trip in all_trips:

        key = (
            trip.get("train_number"),
            trip.get("departure_datetime"),
            trip.get("arrival_datetime"),
        )

        if key not in unique_trips:
            unique_trips[key] = trip

    trips = list(
        unique_trips.values()
    )

    # -----------------------------------------------------
    # Tri par heure de départ
    # -----------------------------------------------------

    trips.sort(
        key=lambda trip: trip.get(
            "departure_datetime",
            "",
        )
    )

    # -----------------------------------------------------
    # MVP : maximum 5 résultats retournés
    # -----------------------------------------------------

    return trips[:5]