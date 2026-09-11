# Smart Mobility Platform

Plateforme Data / IA de mobilité ferroviaire inspirée des problématiques
rencontrées par les plateformes de transport : collecte et
transformation de données, recherche de trajets, analyse décisionnelle,
prédiction de retard et assistant conversationnel.

> Projet de démonstration académique et portfolio. Smart Mobility n'est
> pas un service officiel SNCF et les documents de démonstration
> utilisés par le RAG ne constituent pas les conditions officielles d'un
> transporteur.

------------------------------------------------------------------------

## 1. Objectif

Smart Mobility a été construit comme une plateforme end-to-end
permettant de couvrir plusieurs métiers Data / IA dans un même projet :

-   Data Engineering : ingestion, transformation, qualité et
    orchestration des données ;
-   Data Analysis : KPI et dashboard Power BI ;
-   Data Science : prédiction du retard moyen d'une liaison ;
-   Backend : exposition des fonctionnalités via FastAPI ;
-   Frontend : recherche de trajets et assistant utilisateur ;
-   GenAI : LLM local, tool calling, mémoire conversationnelle et RAG ;
-   Cloud / industrialisation : Azure Data Lake, Docker, Airflow et CI.

L'objectif n'est pas de reproduire SNCF Connect, mais de construire une
architecture réaliste autour de données ferroviaires.
## Architecture

![Architecture Smart Mobility](docs/architecture-smart-mobility.png)
------------------------------------------------------------------------

## 2. Fonctionnalités principales

### Recherche de trajets

L'utilisateur peut :

-   rechercher une gare à partir d'une ville ;
-   sélectionner une gare de départ et d'arrivée ;
-   rechercher des trajets à une date et après une heure donnée ;
-   consulter les détails des trajets disponibles.

Les données horaires proviennent du GTFS SNCF utilisé par le projet.

### Dashboard Data Analyst

Un dashboard Power BI permet notamment d'étudier :

-   les gares avec le plus de passages de trains ;
-   les liaisons les plus fréquentes ;
-   les durées moyennes par liaison ;
-   les départs par heure ;
-   les gares générant le plus de départs.

Important : ces indicateurs représentent l'offre et les circulations
théoriques GTFS. Ils ne représentent pas une fréquentation réelle de
voyageurs.

### Prédiction de retard

Un modèle Random Forest prédit le **retard moyen d'une liaison pour un
mois donné**.

Le modèle ne prédit pas le retard exact d'un train individuel.

Features temporelles principales :

-   retard du mois précédent ;
-   moyenne des 3 observations précédentes ;
-   moyenne des 6 observations précédentes ;
-   mois ;
-   durée moyenne ;
-   volume de trains prévu ;
-   gares et type de service.

Évaluation temporelle :

-   entraînement : données jusqu'à décembre 2024 ;
-   test : données à partir de janvier 2025.

Résultats du modèle final :

  Métrique         Valeur
  ---------- ------------
  MAE          \~2.52 min
  RMSE         \~3.61 min
  R²              \~0.395

Le modèle est enregistré avec Joblib et chargé par FastAPI.

### Assistant IA local

L'assistant utilise **Qwen2.5 3B Instruct** avec Ollama.

Il dispose de trois capacités métier :

1.  `search_trips` --- recherche de trajets ;
2.  `predict_delay` --- appel du modèle ML ;
3.  `search_knowledge` --- recherche dans la documentation via RAG.

La mémoire conversationnelle est persistée dans PostgreSQL. L'assistant
peut donc réutiliser des informations déjà données dans une
conversation.

Exemple :

``` text
Utilisateur : Je veux aller de Paris à Lyon le 8 septembre après 18h.
Utilisateur : Et après 20h ?
```

La seconde demande peut réutiliser la liaison et la date du contexte
précédent.

### RAG documentaire

Le RAG local utilise :

-   `nomic-embed-text` pour les embeddings ;
-   une recherche par similarité cosinus ;
-   une petite base documentaire Smart Mobility.

Le backend utilise également un routage déterministe pour certaines
intentions documentaires afin d'éviter qu'un petit LLM réponde de
lui-même avec des informations non présentes dans les documents.

------------------------------------------------------------------------

## 3. Architecture

``` text
                         UTILISATEUR
                              |
                        React + Vite
                              |
                           FastAPI
                 _____________|______________
                |             |              |
                |             |              |
          PostgreSQL     Modèle ML      Assistant IA
                |        Random Forest       |
                |                            |
             GTFS                     Qwen2.5 3B
                                             |
                         ____________________|____________________
                        |                    |                    |
                  search_trips         predict_delay       search_knowledge
                        |                    |                    |
                  GTFS / API             ML API                  RAG
                                                                  |
                                                         nomic-embed-text


        DATA ENGINEERING / CLOUD
                    |
              SNCF GTFS source
                    |
                 Airflow
                    |
        download -> raw Azure Data Lake
                    |
              transformations
                    |
                PostgreSQL
                    |
              Data Quality
                    |
                Parquet
                    |
           processed Azure Data Lake
```

------------------------------------------------------------------------

## 4. Stack technique

### Backend

-   Python
-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Pydantic

### Frontend

-   React
-   Vite
-   JavaScript

### Data Engineering

-   Python
-   Pandas
-   Apache Airflow
-   Docker
-   GTFS

### Data Analysis

-   SQL
-   PostgreSQL
-   Power BI

### Machine Learning

-   Pandas
-   scikit-learn
-   Random Forest
-   Linear Regression
-   Joblib

### IA générative

-   Ollama
-   Qwen2.5 3B Instruct
-   nomic-embed-text
-   Tool Calling
-   RAG
-   mémoire PostgreSQL

### Cloud / Industrialisation

-   Azure Data Lake Storage Gen2
-   Docker / Docker Compose
-   GitHub Actions
-   tests automatisés

------------------------------------------------------------------------

## 5. Organisation du projet

``` text
smart-mobility/
|
|-- backend/
|   |-- app/
|   |   |-- routers/
|   |   |-- services/
|   |   |   `-- llm/
|   |   |       |-- assistant_service.py
|   |   |       |-- tool_registry.py
|   |   |       |-- tools.py
|   |   |       |-- conversation_memory.py
|   |   |       `-- rag/
|   |   |           |-- rag_service.py
|   |   |           `-- documents/
|   |   `-- models.py
|   `-- .venv/
|
|-- frontend/
|   `-- src/
|       `-- components/
|
|-- data_pipeline/
|   |-- ingestion/
|   |-- transformation/
|   |-- loading/
|   |-- quality/
|   |-- monitoring/
|   |-- raw/
|   |-- clean/
|   `-- processed/
|
|-- data_science/
|   |-- data/
|   |-- notebooks/
|   |-- models/
|   `-- src/
|
|-- airflow/
|   |-- dags/
|   |-- Dockerfile
|   `-- docker-compose.yaml
|
`-- README.md
```

------------------------------------------------------------------------

## 6. Pipeline Data Engineering

Le pipeline Airflow principal suit cette logique :

``` text
download_gtfs
      |
upload_raw_to_azure
      |
extract_gtfs
      |
transform / load stations
      |
transform / load stop_points
      |
transform / load routes
      |
transform / load trips
      |
transform / load stop_times
      |
transform / load calendar_dates
      |
check_data_quality
      |
collect_pipeline_metrics
      |
export_parquet
      |
upload_processed_to_azure
```

Des traitements par chunks sont utilisés pour les volumes importants,
notamment `stop_times`.

------------------------------------------------------------------------

## 7. Qualité et monitoring

Le pipeline inclut des contrôles de volumétrie sur les principales
tables.

Exemples de seuils utilisés :

``` text
stations        >= 3 000
stop_points     >= 5 000
routes          >= 500
trips           >= 30 000
stop_times      >= 300 000
calendar_dates  >= 100 000
```

Les métriques du pipeline sont également collectées afin de contrôler
son état.

------------------------------------------------------------------------

## 8. Installation et lancement

### Prérequis

-   Python
-   Node.js / npm
-   PostgreSQL
-   Docker Desktop
-   Ollama
-   Git

Le projet utilise des variables d'environnement pour les connexions
PostgreSQL et Azure. Les fichiers `.env` et les secrets ne doivent
jamais être versionnés.

### Ordre recommandé

``` text
Docker Desktop
      |
PostgreSQL
      |
Airflow
      |
Ollama
      |
FastAPI
      |
React / Vite
```

### Airflow

``` powershell
cd "C:\Users\ryana\Desktop\The_ Box\smart-mobility\airflow"
docker compose up -d
docker compose ps
```

Interface :

``` text
http://localhost:8080
```

### Backend

``` powershell
cd "C:\Users\ryana\Desktop\The_ Box\smart-mobility\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Swagger :

``` text
http://127.0.0.1:8000/docs
```

### Ollama

Vérifier les modèles :

``` powershell
ollama list
```

Modèles nécessaires :

``` text
qwen2.5:3b
nomic-embed-text
```

Si nécessaire :

``` powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

### Frontend

``` powershell
cd "C:\Users\ryana\Desktop\The_ Box\smart-mobility\frontend"
npm run dev
```

Application :

``` text
http://localhost:5173
```

------------------------------------------------------------------------

## 9. API

Documentation interactive :

``` text
http://127.0.0.1:8000/docs
```

Exemples de capacités exposées :

``` text
GET  /stations
GET  /stations/search
GET  /trips/search
POST /predictions/delay
POST /predictions/delay/route
POST /assistant/chat
```

------------------------------------------------------------------------

## 10. Cloud Azure

Le projet utilise Azure Data Lake Storage Gen2 avec deux zones
principales :

``` text
raw/
processed/
```

La zone `raw` conserve les données sources et la zone `processed` reçoit
les exports transformés, notamment au format Parquet.

Les identifiants et clés Azure restent dans les variables
d'environnement locales et ne doivent pas être présents dans Git.

------------------------------------------------------------------------

## 11. CI et tests

Une pipeline GitHub Actions permet de vérifier notamment :

-   la syntaxe Python ;
-   les tests automatisés ;
-   la stabilité de certaines fonctions du pipeline.

Le projet contient également des tests utilisant `pytest`.

------------------------------------------------------------------------

## 12. Démonstration recommandée

Une démonstration courte peut suivre ce scénario :

1.  montrer Airflow et le pipeline ETL ;
2.  montrer le dashboard Power BI ;
3.  ouvrir l'application React ;
4.  rechercher un trajet Paris -\> Lyon ;
5.  afficher les détails d'un trajet ;
6.  demander une prédiction de retard ;
7.  poser une question documentaire à l'assistant ;
8.  montrer Swagger et l'architecture backend.

Cela permet de présenter successivement Data Engineering, Data Analysis,
Data Science, développement logiciel et IA générative.

------------------------------------------------------------------------

## 13. Limites actuelles

Le projet est un MVP et certaines limites sont volontairement assumées :

-   les horaires GTFS sont théoriques et ne constituent pas du temps
    réel ;
-   le modèle ML prédit un retard moyen mensuel par liaison, pas le
    retard exact d'un train ;
-   la correspondance entre noms de gares GTFS et AQST reste
    partiellement normalisée ;
-   le RAG utilise actuellement une petite documentation de
    démonstration ;
-   Qwen2.5 3B est un petit modèle local et son tool calling n'est pas
    toujours fiable ;
-   certaines intentions sont donc routées de manière déterministe par
    le backend ;
-   la mémoire conversationnelle doit être limitée ou résumée pour une
    utilisation à grande échelle ;
-   le frontend utilise encore une gestion de session à améliorer avant
    une mise en production ;
-   l'application ne gère pas encore les données GTFS-RT temps réel.

------------------------------------------------------------------------

## 14. Améliorations possibles

### Temps réel

Collecter GTFS-RT sur plusieurs mois afin de construire un historique au
niveau du train et permettre une prédiction beaucoup plus fine.

### Machine Learning

Ajouter :

-   météo ;
-   perturbations ;
-   calendrier ;
-   événements ;
-   historique par train ;
-   modèles de gradient boosting.

### IA

Améliorer l'assistant avec :

-   un modèle local plus performant ;
-   un routeur d'intentions structuré ;
-   une sortie JSON contrôlée ;
-   une fenêtre mémoire maîtrisée ;
-   détection des appels d'outils dupliqués ;
-   une base documentaire plus riche ;
-   une base vectorielle si le volume documentaire augmente.

### Production

Ajouter :

-   authentification ;
-   observabilité ;
-   gestion des utilisateurs ;
-   sessions uniques par navigateur ;
-   migrations Alembic ;
-   déploiement cloud complet ;
-   monitoring des modèles.

------------------------------------------------------------------------

## 15. Compétences démontrées

Ce projet met en pratique :

-   conception d'architecture Data / IA ;
-   développement Python ;
-   SQL et modélisation PostgreSQL ;
-   conception ETL ;
-   orchestration Airflow ;
-   Docker ;
-   Azure Data Lake ;
-   analyse de données ;
-   Power BI ;
-   feature engineering ;
-   Machine Learning ;
-   évaluation temporelle ;
-   API REST avec FastAPI ;
-   React ;
-   LLM local ;
-   tool calling ;
-   RAG ;
-   embeddings ;
-   gestion des hallucinations ;
-   CI / tests ;
-   Git / GitHub.

------------------------------------------------------------------------

## 16. Positionnement

Smart Mobility est volontairement conçu comme un projet transversal.

Il montre comment plusieurs briques peuvent être reliées dans une même
plateforme :

``` text
DATA
 |
 +-- Data Engineering
 |
 +-- Data Analysis
 |
 +-- Machine Learning
 |
 +-- Cloud
 |
 +-- Backend / API
 |
 +-- Frontend
 |
 `-- Generative AI
```

Le résultat est une plateforme démontrant un cycle Data / IA complet,
depuis l'ingestion des données jusqu'à leur exploitation par un
utilisateur final.

------------------------------------------------------------------------

## Auteur

**Ryan Aba**

Projet Data / IA --- Smart Mobility
