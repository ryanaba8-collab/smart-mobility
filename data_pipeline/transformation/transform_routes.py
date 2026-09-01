from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent

ROUTES_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "routes.txt"
OUTPUT_FILE = BASE_DIR / "clean" / "routes.csv"


def transform_routes():
    import pandas as pd
    print("Lecture des routes RAW...")

    routes = pd.read_csv(ROUTES_FILE)

    print(f"Routes RAW : {len(routes)}")

    routes = routes[
        [
            "route_id",
            "agency_id",
            "route_short_name",
            "route_long_name",
            "route_type",
            "route_color",
            "route_text_color",
        ]
    ].copy()

    routes = routes.rename(
        columns={
            "route_id": "external_id",
            "route_short_name": "short_name",
            "route_long_name": "long_name",
            "route_color": "color",
            "route_text_color": "text_color",
        }
    )

    routes = routes.dropna(
        subset=[
            "external_id",
            "route_type",
        ]
    )

    routes = routes.drop_duplicates(
        subset=["external_id"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    routes.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Routes transformées : {len(routes)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_routes()