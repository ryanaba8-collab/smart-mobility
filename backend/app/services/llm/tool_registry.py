from app.services.llm.tools import (
    predict_delay,
    search_trips,
)

from app.services.llm.rag.rag_service import (
    search_knowledge,
)

import requests


# =========================================================
# TOOL 1 — PREDICTION DE RETARD
# =========================================================

predict_delay_tool = {
    "type": "function",
    "function": {
        "name": "predict_delay",
        "description": (
            "Prédit le retard moyen et le niveau de risque "
            "d'une liaison ferroviaire pour un mois donné. "
            "Les gares précises de départ et d'arrivée doivent "
            "être connues. Les informations peuvent être déduites "
            "de l'historique lorsque l'utilisateur parle de "
            "'cette liaison', 'ce trajet', 'ce voyage' ou d'un "
            "trajet précédemment affiché."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "annee": {
                    "type": "integer",
                    "description": (
                        "Année de la prédiction. "
                        "Peut être récupérée depuis le message actuel "
                        "ou le contexte de la conversation."
                    ),
                },
                "mois": {
                    "type": "integer",
                    "description": (
                        "Mois de la prédiction entre 1 et 12."
                    ),
                },
                "gare_depart": {
                    "type": "string",
                    "description": (
                        "Nom précis de la gare de départ. "
                        "Réutiliser la gare mentionnée précédemment "
                        "si l'utilisateur fait référence à une "
                        "liaison déjà discutée."
                    ),
                },
                "gare_arrivee": {
                    "type": "string",
                    "description": (
                        "Nom précis de la gare d'arrivée. "
                        "Réutiliser la gare mentionnée précédemment "
                        "si l'utilisateur fait référence à une "
                        "liaison déjà discutée."
                    ),
                },
            },
            "required": [
                "annee",
                "mois",
                "gare_depart",
                "gare_arrivee",
            ],
        },
    },
}


# =========================================================
# TOOL 2 — RECHERCHE DE TRAJETS
# =========================================================

search_trips_tool = {
    "type": "function",
    "function": {
        "name": "search_trips",
        "description": (
            "Recherche les prochains trajets ferroviaires entre "
            "deux villes ou deux gares à une date donnée et après "
            "une heure donnée. Les informations déjà présentes "
            "dans l'historique doivent être réutilisées lorsque "
            "l'utilisateur dit par exemple 'et après 20h ?'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "departure": {
                    "type": "string",
                    "description": (
                        "Ville ou gare de départ, par exemple Paris "
                        "ou Paris Gare de Lyon."
                    ),
                },
                "arrival": {
                    "type": "string",
                    "description": (
                        "Ville ou gare d'arrivée, par exemple Lyon "
                        "ou Lyon Part Dieu."
                    ),
                },
                "travel_date": {
                    "type": "string",
                    "description": (
                        "Date du voyage au format YYYY-MM-DD. "
                        "Réutiliser la date précédente si elle "
                        "est toujours applicable."
                    ),
                },
                "departure_after": {
                    "type": "string",
                    "description": (
                        "Heure minimale de départ au format HH:MM."
                    ),
                },
            },
            "required": [
                "departure",
                "arrival",
                "travel_date",
                "departure_after",
            ],
        },
    },
}


# =========================================================
# TOOL 3 — RAG / BASE DOCUMENTAIRE
# =========================================================

search_knowledge_tool = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": (
            "Recherche des informations dans la base documentaire "
            "Smart Mobility. Utiliser cet outil pour répondre aux "
            "questions concernant les règles, les bagages, "
            "les billets, les annulations, les retards, "
            "l'assistance ou toute autre information présente "
            "dans la documentation Smart Mobility."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Question ou sujet à rechercher dans "
                        "la documentation Smart Mobility."
                    ),
                },
            },
            "required": [
                "query",
            ],
        },
    },
}


# =========================================================
# LISTE DES TOOLS DISPONIBLES POUR QWEN
# =========================================================

tools = [
    predict_delay_tool,
    search_trips_tool,
    search_knowledge_tool,
]


# =========================================================
# EXECUTION DES TOOLS
# =========================================================

def execute_tool(
    function_name: str,
    arguments: dict,
):
    try:

        # -------------------------------------------------
        # Prédiction ML
        # -------------------------------------------------

        if function_name == "predict_delay":
            return predict_delay(
                **arguments
            )

        # -------------------------------------------------
        # Recherche de trajets
        # -------------------------------------------------

        if function_name == "search_trips":
            return search_trips(
                **arguments
            )

        # -------------------------------------------------
        # Recherche documentaire RAG
        # -------------------------------------------------

        if function_name == "search_knowledge":
            return search_knowledge(
                query=arguments["query"]
            )

        # -------------------------------------------------
        # Tool inconnu
        # -------------------------------------------------

        return {
            "success": False,
            "error_type": "unknown_tool",
            "detail": (
                f"Tool inconnu : {function_name}"
            ),
        }

    # =====================================================
    # ERREURS HTTP
    # =====================================================

    except requests.exceptions.HTTPError as exc:

        status_code = None
        detail = None

        if exc.response is not None:

            status_code = (
                exc.response.status_code
            )

            try:
                detail = (
                    exc.response.json()
                )

            except ValueError:
                detail = (
                    exc.response.text
                )

        return {
            "success": False,
            "error_type": "http_error",
            "status_code": status_code,
            "detail": detail,
        }

    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error_type": "timeout",
            "detail": (
                "Le service a mis trop de temps "
                "à répondre."
            ),
        }

    # =====================================================
    # ERREUR DE REQUÊTE
    # =====================================================

    except requests.exceptions.RequestException as exc:

        return {
            "success": False,
            "error_type": "request_error",
            "detail": str(exc),
        }

    # =====================================================
    # ERREUR DE VALIDATION
    # =====================================================

    except ValueError as exc:

        return {
            "success": False,
            "error_type": "validation_error",
            "detail": str(exc),
        }

    # =====================================================
    # ERREUR INATTENDUE
    # =====================================================

    except Exception as exc:

        return {
            "success": False,
            "error_type": "internal_tool_error",
            "detail": str(exc),
        }