# Création des dates du jeu de démo (une ligne par jour)
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
dates = pd.date_range("2026-02-01", "2026-11-17", freq="D")
demo = pd.DataFrame({"Date (AAAA-MM-JJ)": dates})
# Colonne sommeil du jeu de démo (valeurs inventées, moyenne 72, écart-type 9)
sommeil = rng.normal(72, 9, len(demo)).round().clip(0, 100)
demo["Garmin: Sleep Score (0-100)"] = sommeil
# Colonne HRV du jeu de démo (liée au sommeil, valeurs inventées)
hrv = 60 + 0.5 * (sommeil - 72) + rng.normal(0, 6, len(demo))
demo["Garmin: HRV moyenne nuit (ms)"] = hrv.round().clip(20, 120)

# Colonnes stress Garmin et FC de repos du jeu de démo (liées au sommeil, valeurs inventées)
stress = 45 - 0.4 * (sommeil - 72) + rng.normal(0, 8, len(demo))
demo["Garmin: Stress moyen (0-100)"] = stress.round().clip(5, 95)

fc_repos = 54 - 0.15 * (sommeil - 72) + rng.normal(0, 3, len(demo))
demo["Garmin: FC repos (bpm)"] = fc_repos.round().clip(40, 75)

# Colonnes stress Garmin et FC de repos du jeu de démo (liées au sommeil, valeurs inventées)
stress = 45 - 0.4 * (sommeil - 72) + rng.normal(0, 8, len(demo))
demo["Garmin: Stress moyen (0-100)"] = stress.round().clip(5, 95)

fc_repos = 54 - 0.15 * (sommeil - 72) + rng.normal(0, 3, len(demo))
demo["Garmin: FC repos (bpm)"] = fc_repos.round().clip(40, 75)

# Colonnes séance, calories actives et pas du jeu de démo (valeurs inventées)
seance = rng.random(len(demo)) < 0.35
calories = np.where(seance, rng.normal(700, 180, len(demo)), rng.normal(180, 80, len(demo)))
demo["Garmin: Calories actives"] = calories.round().clip(20, 1100)

pas = np.where(seance, rng.normal(10000, 2500, len(demo)), rng.normal(7000, 2500, len(demo)))
demo["Garmin: Pas"] = pas.round().clip(1500, 20000)

# Colonne Body Battery min du jeu de démo (liée au sommeil et à la HRV, valeurs inventées)
sommeil_demo = demo["Garmin: Sleep Score (0-100)"]
hrv_demo = demo["Garmin: HRV moyenne nuit (ms)"]
body_battery = 75 + 0.6 * (sommeil_demo - 72) + 0.4 * (hrv_demo - 60) + rng.normal(0, 5, len(demo))
demo["Garmin: Body Battery min (0-100)"] = body_battery.round().clip(5, 100)

# Colonne énergie du jeu de démo (estimée avant le 10 octobre, ressentie depuis)
dates_demo = demo["Date (AAAA-MM-JJ)"]
bb_demo = demo["Garmin: Body Battery min (0-100)"]

avant = dates_demo < "2026-10-10"
energie_estimee = bb_demo / 10
energie_ressentie = bb_demo / 10 + 0.5 + rng.normal(0, 1.2, len(demo))
energie = np.where(avant, energie_estimee, energie_ressentie)
demo["Introspection: Énergie perçue (1-10)"] = energie.round(1).clip(1, 10)

# Colonne stress perçu du jeu de démo (note entière, liée à l'énergie, valeurs inventées)
energie_demo = demo["Introspection: Énergie perçue (1-10)"]
stress_percu = 4 - 0.5 * (energie_demo - 6.5) + rng.normal(0, 1.5, len(demo))
demo["Introspection: Stress perçu (1-10)"] = stress_percu.round().clip(1, 10)

# Colonnes humeur, heures travaillées et intensité du jeu de démo (valeurs inventées)
humeur = 7 + 0.2 * (energie_demo - 6.5) + rng.normal(0, 0.7, len(demo))
demo["Introspection: Humeur (1-10)"] = humeur.round().clip(1, 10)

heures = 4 + 0.4 * (energie_demo - 6.5) + rng.normal(0, 1.9, len(demo))
demo["Charge: Heures travaillées"] = heures.round(1).clip(0, 10)

intensite = 5 + 0.3 * (heures - 4) + rng.normal(0, 1.5, len(demo))
demo["Charge: Intensité perçue (1-10)"] = intensite.round().clip(1, 10)

## Colonnes mesures corporelles du jeu de démo (valeurs génériques, inventées)
demo["Poids (kg)"] = rng.normal(65, 0.6, len(demo)).round(1)
demo["MGC (kg)"] = rng.normal(18, 0.4, len(demo)).round(1)
demo["MMC (kg)"] = rng.normal(26, 0.3, len(demo)).round(1)
demo["Masse musculaire (kg)"] = rng.normal(44, 0.4, len(demo)).round(1)

# Colonnes texte laissées vides dans la démo
demo["Notes libres"] = ""
demo["Source note (Notion/Excel/Autre)"] = ""

# Enregistrement du jeu de démo avec un onglet Daily_Log
demo.to_excel("data/demo/demo-tracker.xlsx", sheet_name="Daily_Log", index=False)
print(demo.shape)