from pathlib import Path

import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


# ============================================================
# CHEMINS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_FILE = (
    PROJECT_ROOT
    / "data_science"
    / "models"
    / "delay_random_forest.joblib"
)

HISTORY_FILE = (
    PROJECT_ROOT
    / "data_science"
    / "data"
    / "processed"
    / "delay_ml_features.csv"
)


# ============================================================
# CHARGEMENT DU MODELE
# ============================================================

print(f"Chargement du modèle ML : {MODEL_FILE}")

model = joblib.load(MODEL_FILE)

print("Modèle ML chargé.")


# ============================================================
# CHARGEMENT DES DONNEES HISTORIQUES
# ============================================================

print(f"Chargement de l'historique : {HISTORY_FILE}")

history_df = pd.read_csv(
    HISTORY_FILE,
    parse_dates=["date"],
)

print(
    f"Historique chargé : {len(history_df)} lignes."
)


# ============================================================
# SCHEMA TECHNIQUE
# ============================================================

class DelayPredictionRequest(BaseModel):
    annee: int

    mois: int = Field(
        ge=1,
        le=12,
    )

    duree_moyenne: float
    nb_train_prevu: int

    retard_mois_precedent: float
    retard_moyen_3_mois: float
    retard_moyen_6_mois: float

    service: str
    gare_depart: str
    gare_arrivee: str


# ============================================================
# SCHEMA METIER
# ============================================================

class RouteDelayPredictionRequest(BaseModel):
    annee: int

    mois: int = Field(
        ge=1,
        le=12,
        description="Mois de prédiction entre 1 et 12",
    )

    gare_depart: str
    gare_arrivee: str


# ============================================================
# ENDPOINT TECHNIQUE
# ============================================================

@router.post("/delay")
def predict_delay(
    request: DelayPredictionRequest,
):
    """
    Endpoint technique.

    Toutes les features ML doivent être fournies manuellement.
    """

    data = pd.DataFrame(
        [
            request.model_dump()
        ]
    )

    prediction = model.predict(data)

    retard_predit = float(
        prediction[0]
    )

    return {
        "gare_depart":
            request.gare_depart,

        "gare_arrivee":
            request.gare_arrivee,

        "retard_moyen_predit":
            round(retard_predit, 2),

        "unite":
            "minutes",
    }


# ============================================================
# ENDPOINT METIER
# ============================================================

@router.post("/delay/route")
def predict_route_delay(
    request: RouteDelayPredictionRequest,
):
    """
    Endpoint métier.

    L'utilisateur fournit uniquement :
    - l'année
    - le mois
    - la gare de départ
    - la gare d'arrivée

    Les variables historiques nécessaires au modèle
    sont calculées automatiquement.
    """

    # ========================================================
    # 1. DATE A PREDIRE
    # ========================================================

    prediction_date = pd.Timestamp(
        year=request.annee,
        month=request.mois,
        day=1,
    )


    # ========================================================
    # 2. HISTORIQUE DE LA LIAISON
    # ========================================================

    route_history = history_df[
        (
            history_df["gare_depart"]
            == request.gare_depart
        )
        &
        (
            history_df["gare_arrivee"]
            == request.gare_arrivee
        )
        &
        (
            history_df["date"]
            < prediction_date
        )
    ].sort_values("date")


    # ========================================================
    # 3. VERIFICATION DE L'HISTORIQUE
    # ========================================================

    if route_history.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun historique disponible "
                "pour cette liaison."
            ),
        )


    # ========================================================
    # 4. DERNIERE OBSERVATION
    # ========================================================

    last_row = route_history.iloc[-1]

    target = (
        "retard_moyen_tous_trains_arrivee"
    )


    # ========================================================
    # 5. FEATURES HISTORIQUES
    # ========================================================

    retard_mois_precedent = float(
        last_row[target]
    )

    retard_moyen_3_mois = float(
        route_history
        .tail(3)[target]
        .mean()
    )

    retard_moyen_6_mois = float(
        route_history
        .tail(6)[target]
        .mean()
    )


    # ========================================================
    # 6. VARIABLES STRUCTURELLES
    # ========================================================

    duree_moyenne = float(
        last_row["duree_moyenne"]
    )

    nb_train_prevu = int(
        last_row["nb_train_prevu"]
    )

    service = str(
        last_row["service"]
    )


    # ========================================================
    # 7. CONSTRUCTION DES FEATURES ML
    # ========================================================

    data = pd.DataFrame(
        [
            {
                "annee":
                    request.annee,

                "mois":
                    request.mois,

                "duree_moyenne":
                    duree_moyenne,

                "nb_train_prevu":
                    nb_train_prevu,

                "retard_mois_precedent":
                    retard_mois_precedent,

                "retard_moyen_3_mois":
                    retard_moyen_3_mois,

                "retard_moyen_6_mois":
                    retard_moyen_6_mois,

                "service":
                    service,

                "gare_depart":
                    request.gare_depart,

                "gare_arrivee":
                    request.gare_arrivee,
            }
        ]
    )


    # ========================================================
    # 8. PREDICTION ML
    # ========================================================

    prediction = model.predict(data)

    retard_predit = float(
        prediction[0]
    )


    # ========================================================
    # 9. NIVEAU DE RISQUE
    # ========================================================

    if retard_predit < 5:
        niveau_risque = "faible"

    elif retard_predit < 10:
        niveau_risque = "modere"

    else:
        niveau_risque = "eleve"


    # ========================================================
    # 10. REPONSE METIER
    # ========================================================

    return {
        "gare_depart":
            request.gare_depart,

        "gare_arrivee":
            request.gare_arrivee,

        "periode_prediction":
            f"{request.annee}-{request.mois:02d}",

        "derniere_donnee_disponible":
            last_row["date"].strftime("%Y-%m"),

        "retard_mois_precedent":
            round(
                retard_mois_precedent,
                2,
            ),

        "retard_moyen_3_mois":
            round(
                retard_moyen_3_mois,
                2,
            ),

        "retard_moyen_6_mois":
            round(
                retard_moyen_6_mois,
                2,
            ),

        "retard_moyen_predit":
            round(
                retard_predit,
                2,
            ),

        "niveau_risque":
            niveau_risque,

        "unite":
            "minutes",
    }