import pandas as pd

def load_data(file):
    """
    Charge les trois DataFrames depuis le fichier Excel :
     - feuille 'Comparatif'
     - feuille 'Entreprise' ou 'Entreprises'
     - feuille 'Alignement avec le besoin'
    """
    # On force l'utilisation d'openpyxl pour gérer correctement tous les formats .xlsx et URL SharePoint
    xls = pd.ExcelFile(file, engine="openpyxl")

    # --- 1) Comparatif ---
    if "Comparatif" not in xls.sheet_names:
        raise ValueError(f"Feuille 'Comparatif' introuvable. Feuilles disponibles : {xls.sheet_names}")
    df_comp = pd.read_excel(
        xls,
        sheet_name="Comparatif",
        engine="openpyxl"
    )

    # --- 2) Entreprise / Entreprises ---
    if "Entreprise" in xls.sheet_names:
        sheet_ent = "Entreprise"
    elif "Entreprises" in xls.sheet_names:
        sheet_ent = "Entreprises"
    else:
        raise ValueError(
            f"Feuille entreprise introuvable. Cherché 'Entreprise' ou 'Entreprises' dans {xls.sheet_names}"
        )
    df_ent = pd.read_excel(
        xls,
        sheet_name=sheet_ent,
        engine="openpyxl"
    )

    # --- 3) Alignement avec le besoin ---
    name_align = "Alignement avec le besoin"
    if name_align not in xls.sheet_names:
        raise ValueError(
            f"Feuille '{name_align}' introuvable. Feuilles disponibles : {xls.sheet_names}"
        )
    df_align = pd.read_excel(
        xls,
        sheet_name=name_align,
        header=0,
        engine="openpyxl"
    )

    # --- Nettoyage basique des colonnes ---
    df_comp.columns  = [col.strip() for col in df_comp.columns]
    df_ent.columns   = [col.strip() for col in df_ent.columns]
    df_align.columns = [col.strip() for col in df_align.columns]

    return df_comp, df_ent, df_align