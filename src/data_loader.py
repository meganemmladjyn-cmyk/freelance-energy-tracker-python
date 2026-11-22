"""Chargement et nettoyage du journal de suivi quotidien (Daily_Log)."""
from pathlib import Path
import pandas as pd

RENAME_MAP = {
    "Date (AAAA-MM-JJ)": "date",
    "Garmin: Sleep Score (0-100)": "garmin_sleep_score",
    "Garmin: HRV moyenne nuit (ms)": "garmin_hrv",
    "Garmin: Stress moyen (0-100)": "garmin_stress",
    "Garmin: Body Battery min (0-100)": "garmin_body_battery_min",
    "Garmin: FC repos (bpm)": "garmin_fc_repos",
    "Garmin: Pas": "garmin_pas",
    "Garmin: Calories actives": "garmin_calories_actives",
    "Poids (kg)": "poids_kg",
    "MGC (kg)": "mgc_kg",
    "MMC (kg)": "mmc_kg",
    "Masse musculaire (kg)": "masse_musculaire_kg",
    "Introspection: Énergie perçue (1-10)": "energie_percue",
    "Introspection: Stress perçu (1-10)": "stress_percu",
    "Introspection: Humeur (1-10)": "humeur",
    "Charge: Heures travaillées": "heures_travaillees",
    "Charge: Intensité perçue (1-10)": "intensite_percue",
    "Notes libres": "notes",
    "Source note (Notion/Excel/Autre)": "source_note",
}


def load_daily_log(path: str | Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Daily_Log")
    df = df.rename(columns=RENAME_MAP)
    df = df.drop(columns=["source_note"], errors="ignore")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"] <= pd.Timestamp.today().normalize()]
    df = df.sort_values("date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = load_daily_log("data/raw/freelance-energy-tracker-template.xlsx")
    debut = df["date"].min().date()
    fin = df["date"].max().date()
    print(f"{len(df)} lignes réelles, du {debut} au {fin}")
    print(df.dtypes)
    print("\nValeurs manquantes par colonne :")
    print(df.isna().sum())

    trous = df[df["energie_percue"].isna()]["date"].dt.date.tolist()
    if trous:
        print(f"\n{len(trous)} jour(s) sans énergie perçue saisie : {trous}")
    else:
        print("\nAucun jour manquant sur énergie perçue dans la période réelle.")
