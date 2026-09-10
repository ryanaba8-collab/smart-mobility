import json

import ollama
from sqlalchemy.orm import Session

from app.services.llm.conversation_memory import (
    get_or_create_conversation,
    get_history,
    save_message,
)
from app.services.llm.tool_registry import (
    tools,
    execute_tool,
)


# =========================================================
# CONFIGURATION
# =========================================================

MAX_TOOL_ROUNDS = 3


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
Tu es l'assistant de Smart Mobility.

Tu disposes de trois outils principaux :

1. search_trips
   Recherche des trajets ferroviaires.

2. predict_delay
   Prédit le retard moyen et le niveau de risque
   d'une liaison ferroviaire pour un mois donné.

3. search_knowledge
   Recherche des informations dans la base documentaire
   Smart Mobility.


=========================================================
RÈGLES GÉNÉRALES
=========================================================

- Utilise les informations présentes dans l'historique
  de conversation.

- Ne demande jamais à l'utilisateur une information
  qui est déjà disponible dans les messages précédents.

- Les expressions comme :
  "cette liaison",
  "ce trajet",
  "ce voyage",
  "le premier train",
  "le deuxième train",
  "et après 20h ?"
  doivent être résolues à partir de l'historique
  lorsque c'est possible.

- N'invente jamais une ville, une gare, une date,
  un horaire, un numéro de train ou un résultat.


=========================================================
RÈGLES POUR LA RECHERCHE DE TRAJETS
=========================================================

- Si l'utilisateur demande des horaires, des trains
  ou des trajets, utilise search_trips.

- search_trips accepte des noms de villes.

Exemple :

Paris -> Lyon

- Il n'est donc pas nécessaire de demander une gare
  précise pour rechercher un trajet.

- Si la date ou l'heure est déjà présente dans
  l'historique, réutilise-la.

- Si search_trips retourne une liste non vide,
  considère que ces trajets existent.

- Ne modifie jamais les horaires, numéros de train
  ou gares retournés par search_trips.


=========================================================
RÈGLES POUR LA PRÉDICTION DE RETARD
=========================================================

- Si l'utilisateur demande un risque ou une prédiction
  de retard, utilise predict_delay.

- predict_delay prédit le retard moyen d'une LIAISON
  pour un MOIS donné.

- predict_delay ne prédit PAS le retard individuel
  d'un train précis.

- Un numéro de train peut servir à identifier
  la liaison choisie par l'utilisateur, mais la
  prédiction reste une prédiction mensuelle de liaison.

- Tu ne peux jamais calculer toi-même une valeur
  de retard.

- Tu ne peux jamais inventer un niveau de risque.

- Toute valeur numérique de retard et tout niveau
  de risque doivent obligatoirement provenir
  d'un appel réussi à predict_delay.

- Dire "je vais utiliser predict_delay" ne signifie PAS
  que predict_delay a été exécuté.

- Ne dis jamais qu'une prédiction a été effectuée
  si aucun résultat réussi de predict_delay
  n'est présent.


=========================================================
PRÉCISION DES GARES POUR predict_delay
=========================================================

- Pour predict_delay, les gares précises de départ
  et d'arrivée doivent être connues.

- Un simple nom de ville n'est pas suffisamment précis.

Exemples trop génériques :

"Paris"
"Lyon"
"Bordeaux"
"Marseille"

- N'appelle jamais predict_delay avec seulement
  des noms de villes génériques.

- Si l'utilisateur fournit seulement des villes
  et demande une prédiction, demande-lui de préciser
  les gares exactes.

- Si les gares exactes sont déjà présentes dans
  l'historique, réutilise-les.

- Si search_trips a retourné plusieurs trajets
  et que l'utilisateur dit :
  "fais la prédiction pour le premier train"
  utilise le premier trajet de la liste pour déterminer
  la gare de départ et la gare d'arrivée.

- Ne demande pas à nouveau les gares si le trajet choisi
  permet déjà de les déterminer.

- Si plusieurs possibilités restent réellement ambiguës,
  demande à l'utilisateur de préciser son choix.


=========================================================
DATES
=========================================================

- Si l'utilisateur mentionne un mois et une année,
  transforme-les correctement en valeurs numériques.

Exemple :

"septembre 2026"

devient :

mois = 9
annee = 2026

- Si le mois et l'année sont déjà connus grâce
  à l'historique, réutilise-les.


=========================================================
MULTI-TOOL
=========================================================

- Une demande peut nécessiter plusieurs outils.

- Si plusieurs actions sont nécessaires,
  utilise les outils nécessaires avant de répondre.

- Si l'utilisateur demande à la fois une recherche
  de trajets et une prédiction de retard,
  commence par search_trips.

- Analyse ensuite le résultat de search_trips.

- Si une liaison précise est connue sans ambiguïté,
  appelle predict_delay.

- Si plusieurs trajets existent et que l'utilisateur
  n'en a choisi aucun, présente les trajets et demande
  lequel il souhaite utiliser pour la prédiction.

- Ne choisis pas arbitrairement un trajet.


=========================================================
ERREURS
=========================================================

- Si un outil retourne "success": false,
  n'invente aucun résultat.

- Explique simplement que l'opération n'a pas pu
  être effectuée.

- Ne révèle pas les exceptions Python,
  les traces techniques internes
  ou les codes d'erreur.

- Ne transforme jamais une erreur d'un outil
  en résultat métier.=========================================================
RÈGLES POUR LA BASE DOCUMENTAIRE / RAG
=========================================================

- Si l'utilisateur pose une question sur :
  les bagages,
  les billets,
  les annulations,
  l'assistance,
  les règles Smart Mobility,
  ou une information documentaire,
  utilise search_knowledge.

- Utilise uniquement les informations retournées
  par search_knowledge pour répondre à ce type de question.

- N'invente pas de règle ou de politique
  qui n'apparaît pas dans les résultats du RAG.

- Si search_knowledge ne retourne aucune information
  pertinente, indique simplement que l'information
  n'est pas disponible dans la documentation Smart Mobility.

- Les documents Smart Mobility utilisés ici sont
  ceux du démonstrateur et ne représentent pas
  nécessairement les règles officielles SNCF.


"""


# =========================================================
# PROMPTS DE GARDE-FOU
# =========================================================

EMPTY_RESPONSE_RETRY_PROMPT = """
Ta réponse précédente était vide.

Analyse précisément la demande utilisateur.

- Pour rechercher un trajet, utilise search_trips.
- Pour une prédiction, utilise predict_delay.
- Pour une question documentaire, utilise search_knowledge.
- Ne donne aucune valeur de retard ou de risque sans
  résultat réel de predict_delay.
- Si les gares précises sont dans l'historique,
  réutilise-les.
- Si l'utilisateur dit "premier train", "deuxième train",
  "ce trajet" ou "cette liaison", retrouve les gares
  correspondantes dans l'historique.
- Si les informations nécessaires manquent réellement,
  demande uniquement l'information manquante.
- Ne réponds jamais avec un message vide.
"""

FINAL_RESPONSE_PROMPT = """
Réponds uniquement à partir des informations et des
résultats présents dans la conversation.

- Ne modifie aucune donnée retournée par les outils.
- N'invente aucune information.
- Pour search_trips, recopie fidèlement numéros de train,
  gares, horaires et statuts.
- Le statut "scheduled" signifie "programmé".
- Pour predict_delay, utilise exactement les valeurs
  retournées par l'outil.
- predict_delay prédit une liaison pour un mois, pas un
  train individuel.
- Si l'utilisateur a choisi un train, ce train sert
  uniquement à identifier la liaison.
- Si predict_delay n'a pas réussi, ne donne aucune valeur
  de prédiction.
- Si un outil retourne success=false, n'invente rien.
- Ne révèle pas les exceptions Python ni les traces internes.
- Réponds de manière naturelle et concise.

- Pour search_knowledge, reformule fidèlement
  les informations retournées par la documentation.

- N'ajoute pas de règle, condition ou politique
  qui n'est pas présente dans les résultats du RAG.

"""

PREDICTION_EXTRACTION_PROMPT = """
Analyse toute la conversation et extrais uniquement les
paramètres nécessaires à predict_delay.

Si l'utilisateur fait référence à :
- "le premier train"
- "le deuxième train"
- "ce trajet"
- "cette liaison"

retrouve les gares correspondantes dans l'historique.

Retourne UNIQUEMENT un JSON valide sous cette forme :

{
  "annee": 2026,
  "mois": 9,
  "gare_depart": "PARIS GARE DE LYON",
  "gare_arrivee": "LYON PART DIEU"
}

Si une information est introuvable, mets null.

N'ajoute aucune explication.
N'effectue aucune prédiction.
N'invente aucune valeur de retard.
"""


# =========================================================
# OUTILS INTERNES DE GARDE-FOU
# =========================================================

def contains_prediction_claim(content: str) -> bool:
    if not content:
        return False

    text = content.lower()

    prediction_keywords = [
        "retard moyen",
        "risque de retard",
        "niveau de risque",
        "prédiction de retard",
        "prediction de retard",
        "retard prévu",
        "retard prevu",
        "retard prédit",
        "retard predit",
    ]

    return any(keyword in text for keyword in prediction_keywords)


def is_knowledge_question(content: str) -> bool:
    if not content:
        return False

    text = content.lower()

    # Une demande de prédiction ne doit PAS partir vers le RAG
    prediction_keywords = [
        "prédiction",
        "prediction",
        "prédire",
        "predire",
        "risque de retard",
        "retard moyen",
        "retard prévu",
        "retard prevu",
        "retard prédit",
        "retard predit",
    ]

    if any(
        keyword in text
        for keyword in prediction_keywords
    ):
        return False

    knowledge_keywords = [
        "bagage",
        "bagages",
        "billet",
        "billets",
        "annulé",
        "annule",
        "annulation",
        "annuler",
        "assistance",
        "règle",
        "règles",
        "regle",
        "regles",
        "retard",
        "en retard",
    ]

    return any(
        keyword in text
        for keyword in knowledge_keywords
    )

def extract_prediction_parameters(messages):
    extraction_messages = [
        *messages,
        {
            "role": "system",
            "content": PREDICTION_EXTRACTION_PROMPT,
        },
    ]

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=extraction_messages,
        format="json",
        options={"temperature": 0},
    )

    content = response["message"].get("content", "")

    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None


# =========================================================
# ASSISTANT SERVICE
# =========================================================

def process_message(
    db: Session,
    session_id: str,
    user_message: str,
):
    # -----------------------------------------------------
    # 1. Conversation + historique
    # -----------------------------------------------------

    conversation = get_or_create_conversation(
        db=db,
        session_id=session_id,
    )

    history = get_history(
        db=db,
        conversation_id=conversation.id,
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *history,
        {
            "role": "user",
            "content": user_message,
        },
    ]

    # =====================================================
    # 2. ROUTAGE RAG DIRECT
    # =====================================================

    if is_knowledge_question(user_message):
        print(
            "Question documentaire détectée "
            "-> RAG direct."
        )

        result = execute_tool(
            function_name="search_knowledge",
            arguments={"query": user_message},
        )

        print("Résultat search_knowledge :", result)

        rag_failed = (
            isinstance(result, dict)
            and result.get("success") is False
        )

        if rag_failed or not result:
            final_text = (
                "Je n'ai pas trouvé cette information "
                "dans la documentation Smart Mobility."
            )
        else:
            rag_context = json.dumps(
                result,
                ensure_ascii=False,
            )

            rag_messages = [
                {
                    "role": "system",
                    "content": (
                        "Tu es l'assistant Smart Mobility. "
                        "Réponds uniquement à partir du contexte "
                        "documentaire fourni. N'ajoute aucune "
                        "information externe, aucun numéro de téléphone, "
                        "aucune règle, aucune politique ni aucun "
                        "remboursement absent du contexte. "
                        "Si le contexte ne permet pas de répondre, "
                        "dis que l'information n'est pas disponible "
                        "dans la documentation Smart Mobility."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
                {
                    "role": "system",
                    "content": (
                        "Contexte documentaire Smart Mobility :\n"
                        + rag_context
                    ),
                },
            ]

            rag_response = ollama.chat(
                model="qwen2.5:3b",
                messages=rag_messages,
                options={"temperature": 0},
            )

            final_text = rag_response["message"].get(
                "content",
                "",
            ).strip()

            if not final_text:
                first_result = result[0]
                if isinstance(first_result, dict):
                    final_text = first_result.get(
                        "content",
                        "",
                    ).strip()

            if not final_text:
                final_text = (
                    "Je n'ai pas trouvé cette information "
                    "dans la documentation Smart Mobility."
                )

        save_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )

        save_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=final_text,
        )

        return final_text

    final_text = None

    # État de la prédiction pendant cette requête
    predict_delay_called = False
    predict_delay_succeeded = False
    predict_delay_result = None

    generic_cities = {
        "paris",
        "lyon",
        "bordeaux",
        "marseille",
        "rennes",
        "lille",
        "nantes",
        "strasbourg",
        "toulouse",
        "montpellier",
    }

    # =====================================================
    # 2. BOUCLE D'ORCHESTRATION
    # =====================================================

    for round_index in range(MAX_TOOL_ROUNDS):
        print(
            f"\n=== ROUND {round_index + 1} / "
            f"{MAX_TOOL_ROUNDS} ==="
        )

        response = ollama.chat(
            model="qwen2.5:3b",
            messages=messages,
            tools=tools,
            options={"temperature": 0},
        )

        assistant_message = response["message"]
        content = assistant_message.get("content", "")
        tool_calls = assistant_message.get("tool_calls")

        # -------------------------------------------------
        # Retry si réponse vide
        # -------------------------------------------------

        if not content and not tool_calls:
            retry_messages = messages + [
                {
                    "role": "system",
                    "content": EMPTY_RESPONSE_RETRY_PROMPT,
                }
            ]

            response = ollama.chat(
                model="qwen2.5:3b",
                messages=retry_messages,
                tools=tools,
                options={"temperature": 0},
            )

            assistant_message = response["message"]
            content = assistant_message.get("content", "")
            tool_calls = assistant_message.get("tool_calls")

        print("\n=== REPONSE BRUTE QWEN ===")
        print(assistant_message)
        print("==========================")

        messages.append(assistant_message)

        print("\n=== TOOL CALLS QWEN ===")
        print(tool_calls)
        print("=======================\n")

        # =================================================
        # 3. QWEN N'APPELLE AUCUN TOOL
        # =================================================

        if not tool_calls:
            if not content:
                continue

            # Si Qwen essaie de donner une prédiction sans
            # avoir réellement appelé predict_delay,
            # Python prend le relais.
            if (
                contains_prediction_claim(content)
                and not predict_delay_succeeded
            ):
                print(
                    "Prédiction détectée sans résultat réel "
                    "-> fallback déterministe."
                )

                prediction_args = extract_prediction_parameters(
                    messages
                )

                print(
                    "Paramètres extraits pour predict_delay :",
                    prediction_args,
                )

                if not prediction_args:
                    final_text = (
                        "Je n'ai pas pu déterminer les informations "
                        "nécessaires pour effectuer la prédiction."
                    )
                    break

                required_fields = [
                    "annee",
                    "mois",
                    "gare_depart",
                    "gare_arrivee",
                ]

                missing_fields = [
                    field
                    for field in required_fields
                    if prediction_args.get(field) is None
                    or prediction_args.get(field) == ""
                ]

                if missing_fields:
                    final_text = (
                        "Il me manque certaines informations pour "
                        "effectuer la prédiction. Peux-tu préciser "
                        "les gares exactes ainsi que le mois concerné ?"
                    )
                    break

                gare_depart = str(
                    prediction_args["gare_depart"]
                ).strip()

                gare_arrivee = str(
                    prediction_args["gare_arrivee"]
                ).strip()

                if (
                    gare_depart.lower() in generic_cities
                    or gare_arrivee.lower() in generic_cities
                ):
                    final_text = (
                        "Pour effectuer la prédiction, j'ai besoin "
                        "des gares exactes de départ et d'arrivée."
                    )
                    break

                predict_delay_called = True

                result = execute_tool(
                    function_name="predict_delay",
                    arguments={
                        "annee": int(prediction_args["annee"]),
                        "mois": int(prediction_args["mois"]),
                        "gare_depart": gare_depart,
                        "gare_arrivee": gare_arrivee,
                    },
                )

                print(
                    "Résultat fallback predict_delay :",
                    result,
                )

                tool_failed = (
                    isinstance(result, dict)
                    and result.get("success") is False
                )

                if tool_failed:
                    final_text = (
                        "Je n'ai pas pu obtenir une prédiction "
                        "fiable pour cette liaison."
                    )
                    break

                predict_delay_succeeded = True
                predict_delay_result = result

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": "predict_delay",
                        "content": json.dumps(
                            result,
                            ensure_ascii=False,
                        ),
                    }
                )

                # Tour suivant : Qwen reformule seulement
                # le résultat réel.
                continue

            final_text = content
            break

        # =================================================
        # 4. EXÉCUTION DES TOOLS DEMANDÉS PAR QWEN
        # =================================================

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            # -------------------------------------------------
            # Protection métier predict_delay
            # -------------------------------------------------

            if function_name == "predict_delay":
                predict_delay_called = True

                gare_depart = str(
                    arguments.get("gare_depart", "")
                ).strip()

                gare_arrivee = str(
                    arguments.get("gare_arrivee", "")
                ).strip()

                if (
                    gare_depart.lower() in generic_cities
                    or gare_arrivee.lower() in generic_cities
                ):
                    result = {
                        "success": False,
                        "error_type": "station_precision_required",
                        "detail": (
                            "La prédiction nécessite les gares "
                            "exactes de départ et d'arrivée."
                        ),
                    }

                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": function_name,
                            "content": json.dumps(
                                result,
                                ensure_ascii=False,
                            ),
                        }
                    )

                    continue

            print("Tool choisi :", function_name)
            print("Arguments :", arguments)

            result = execute_tool(
                function_name=function_name,
                arguments=arguments,
            )

            print("Résultat du tool :", result)

            if function_name == "predict_delay":
                tool_failed = (
                    isinstance(result, dict)
                    and result.get("success") is False
                )

                if not tool_failed:
                    predict_delay_succeeded = True
                    predict_delay_result = result

            messages.append(
                {
                    "role": "tool",
                    "tool_name": function_name,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

    # =====================================================
    # 5. RÉPONSE FINALE SI AUCUN TEXTE N'A ÉTÉ PRODUIT
    # =====================================================

    if final_text is None:
        if predict_delay_succeeded:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Un appel réel à predict_delay a réussi. "
                        "Voici son résultat exact : "
                        + json.dumps(
                            predict_delay_result,
                            ensure_ascii=False,
                        )
                        + "\nUtilise uniquement ces valeurs."
                    ),
                }
            )

        messages.append(
            {
                "role": "system",
                "content": FINAL_RESPONSE_PROMPT,
            }
        )

        final_response = ollama.chat(
            model="qwen2.5:3b",
            messages=messages,
            options={"temperature": 0},
        )

        final_text = final_response["message"].get(
            "content",
            "",
        )

    # =====================================================
    # 6. DERNIÈRE PROTECTION ANTI-HALLUCINATION
    # =====================================================

    if (
        final_text
        and contains_prediction_claim(final_text)
        and not predict_delay_succeeded
    ):
        if predict_delay_called:
            final_text = (
                "Je n'ai pas pu obtenir une prédiction fiable "
                "à partir du modèle. Je ne vais donc pas "
                "inventer de résultat."
            )
        else:
            final_text = (
                "Pour fournir une prédiction de retard, "
                "je dois d'abord exécuter le modèle avec "
                "une gare de départ et une gare d'arrivée "
                "précises."
            )

    # =====================================================
    # 7. PROTECTION RÉPONSE VIDE
    # =====================================================

    if not final_text:
        final_text = (
            "Je n'ai pas pu produire une réponse complète "
            "à partir des informations disponibles."
        )

    # =====================================================
    # 8. SAUVEGARDE POSTGRESQL
    # =====================================================

    save_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=user_message,
    )

    save_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=final_text,
    )

    return final_text
