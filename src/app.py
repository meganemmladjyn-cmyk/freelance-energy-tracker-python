# Dashboard de suivi énergie, version à deux onglets
from pathlib import Path
import streamlit as st
# Import des librairies de visualisation
import matplotlib.pyplot as plt
import seaborn as sns

# Chargement de Poppins depuis le projet pour les graphiques matplotlib
from matplotlib import font_manager

font_manager.fontManager.addfont("assets/fonts/Poppins-Regular.ttf")
font_manager.fontManager.addfont("assets/fonts/Poppins-SemiBold.ttf")
plt.rcParams["font.family"] = "Poppins"

from data_loader import load_daily_log


st.set_page_config(page_title="Suivi énergie freelance", layout="wide")

# Choix de la source : Excel réel s'il existe, sinon jeu de démo
CHEMIN_REEL = Path("data/raw/freelance-energy-tracker-template.xlsx")
CHEMIN_DEMO = Path("data/demo/demo-tracker.xlsx")
mode_demo = not CHEMIN_REEL.exists()
DATA_PATH = CHEMIN_DEMO if mode_demo else CHEMIN_REEL
SEUIL_ALERTE = 4

with st.sidebar:
    st.header("Suivi énergie")
    if st.button("🔄 Actualiser"):
        st.rerun()
    st.caption("Relit le fichier Excel à chaque clic.")

    # Indication de la source affichée
    if mode_demo:
        st.info("Données de démonstration, générées par le code.")

df = load_daily_log(DATA_PATH)
# Création de la colonne saisie_ressenti (True à partir du 10 octobre)
df["saisie_ressenti"] = df["date"] >= "2026-10-10"
# Création de la colonne periode (noms lisibles pour la légende)
df["Periode"] = df["saisie_ressenti"].map({False: "Énergie estimée", True: "Énergie ressentie"})
derniere_date = df["date"].max().date()

# Bandeau d'en-tête en dégradé, aux couleurs de la charte
st.markdown(
    """
    <div class="bandeau">
        <h1>Suivi énergie freelance</h1>
        <p>Croiser ressenti et données Garmin pour repérer les signaux de surmenage.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Fichier à jour jusqu'au {derniere_date} (dernière ligne, saisie ou vide)")

df["moyenne_7j"] = df["energie_percue"].rolling(7).mean()

# Création des deux onglets
onglet_energie, onglet_facteurs = st.tabs(["Énergie", "Facteurs"])

with onglet_energie:
    st.subheader("Énergie perçue")
        # Courbe de l'énergie aux couleurs de la charte, légende lisible
    donnees_courbe = df.set_index("date")[["energie_percue", "moyenne_7j"]].rename(
        columns={"energie_percue": "Énergie du jour", "moyenne_7j": "Moyenne sur 7 jours"}
    )
    st.line_chart(donnees_courbe, color=["#C4B5FD", "#4F46E5"])

    df_energie_saisie = df.dropna(subset=["energie_percue"])
    sous_seuil = df_energie_saisie["energie_percue"] < SEUIL_ALERTE
    trois_jours = sous_seuil.rolling(3).sum() >= 3

    if trois_jours.iloc[-1]:
        derniere_alerte = df_energie_saisie["date"].iloc[-1].date()
        st.warning(f"Trois jours consécutifs sous le seuil d'énergie perçue (jusqu'au {derniere_alerte}).")
    else:
        st.success("Aucune alerte sur les trois derniers jours renseignés.")

    colonnes_snapshot = ["energie_percue", "stress_percu", "heures_travaillees"]
    derniere_ligne = df.dropna(subset=colonnes_snapshot).iloc[-1]
    date_snapshot = derniere_ligne["date"].date()

    st.caption(f"Indicateurs du {date_snapshot} (dernier jour où les trois métriques sont renseignées)")
        # Moyenne des 7 jours qui précèdent la date des indicateurs
    position = derniere_ligne.name
    semaine_precedente = df.loc[position - 7 : position - 1]

    ecart_energie = derniere_ligne["energie_percue"] - semaine_precedente["energie_percue"].mean()
    ecart_stress = derniere_ligne["stress_percu"] - semaine_precedente["stress_percu"].mean()
    ecart_heures = derniere_ligne["heures_travaillees"] - semaine_precedente["heures_travaillees"].mean()

    # Cartes avec l'écart à la moyenne des 7 jours précédents
    col1, col2, col3 = st.columns(3)
    col1.metric("Énergie perçue", f"{derniere_ligne['energie_percue']:.1f}/10", f"{ecart_energie:+.1f} vs 7 j")
    col2.metric("Stress perçu", f"{derniere_ligne['stress_percu']:.1f}/10", f"{ecart_stress:+.1f} vs 7 j", delta_color="inverse")
    col3.metric("Heures travaillées", f"{derniere_ligne['heures_travaillees']:.1f} h", f"{ecart_heures:+.1f} h vs 7 j", delta_color="off")

with onglet_facteurs:
        # Liste des facteurs : texte affiché, puis nom de la colonne
    facteurs = {
        "Sommeil (score Garmin)": "garmin_sleep_score",
        "HRV (ms)": "garmin_hrv",
        "Stress Garmin": "garmin_stress",
        "FC de repos (bpm)": "garmin_fc_repos",
        "Stress perçu": "stress_percu",
    }

    # Liste déroulante pour choisir le facteur à comparer avec l'énergie
    choix = st.selectbox("Facteur à comparer avec l'énergie", list(facteurs.keys()))
    colonne = facteurs[choix]

        # Graphique du facteur choisi : bandes pour le stress perçu, nuage pour les autres
        # Couleurs de la charte pour les deux périodes de saisie
    couleurs_periode = {"Énergie estimée": "#A78BFA", "Énergie ressentie": "#22D3EE"}

    # Graphique du facteur choisi : bandes pour le stress perçu, nuage pour les autres
        # Graphique du facteur choisi : bandes pour le stress perçu, nuage pour les autres
    fig_facteur, ax_facteur = plt.subplots()

    # Fond du graphique assorti à la page
    fig_facteur.patch.set_facecolor("#F6F5FF")
    ax_facteur.set_facecolor("#F6F5FF")

    if colonne == "stress_percu":
        sns.stripplot(data=df, x=colonne, y="energie_percue", hue="Periode", palette=couleurs_periode, dodge=True, ax=ax_facteur)
    else:
        sns.scatterplot(data=df, x=colonne, y="energie_percue", hue="Periode", palette=couleurs_periode, ax=ax_facteur)

    # Cadre allégé et titres des axes lisibles
    sns.despine(ax=ax_facteur)
    ax_facteur.set_xlabel(choix)
    ax_facteur.set_ylabel("Énergie perçue (1-10)")
    st.pyplot(fig_facteur)

    st.caption("Avant le 10 octobre, l'énergie est estimée depuis le Body Battery. Depuis, elle suit mon ressenti.")


    # Style du dashboard : police Poppins, titre en dégradé, cartes à accent cyan, bandeau d'en-tête
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {
        font-family: 'Poppins', sans-serif;
    }

    .stApp h1 {
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        -webkit-background-clip: text;
        color: transparent;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border-left: 4px solid #22D3EE;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(91, 75, 219, 0.12);
    }

    .bandeau {
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 16px;
    }
    .bandeau h1 {
        color: #FFFFFF !important;
        background: none !important;
        -webkit-background-clip: border-box !important;
        margin: 0;
    }
    .bandeau p {
        color: #E0E7FF;
        margin: 6px 0 0 0;
    }
        /* Barre latérale en dégradé vertical, texte en blanc */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4F46E5, #7C3AED);
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #FFFFFF !important;
    }

        /* Onglets en pastilles : tous arrondis, l'actif en bleu-violet */
    button[data-baseweb="tab"] {
        border-radius: 999px;
        padding: 6px 18px;
        margin-right: 8px;
        background: #E8E6FB;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #5B4BDB;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #FFFFFF !important;
    }
    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] {
        display: none;
    }

        /* Masquage de l'interface Streamlit pour un rendu de produit fini */
    #MainMenu {
        visibility: hidden;
    }
    header [data-testid="stDecoration"] {
        display: none;
    }
    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
    



    


