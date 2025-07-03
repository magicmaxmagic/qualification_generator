import pandas as pd

def load_data(file):
    """Charge les données depuis un fichier Excel streamlit"""
    df_comp = pd.read_excel(file, sheet_name="Comparatif")
    df_ent = pd.read_excel(file, sheet_name="Entreprises")
    df_align = pd.read_excel(file, sheet_name="Alignement avec le besoin")

    # Nettoyage
    df_comp.columns = [col.strip() for col in df_comp.columns]
    df_ent.columns = [col.strip() for col in df_ent.columns]
    df_align.columns = [col.strip() for col in df_align.columns]

    return df_comp, df_ent, df_align