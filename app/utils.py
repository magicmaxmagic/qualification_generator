import pandas as pd

def load_data(file):
    """
    Charge les quatre DataFrames principaux depuis le fichier Excel :
     - feuille 'Analyse comparative' (au lieu de 'Comparatif')
     - feuille 'Entreprise' ou 'Entreprises'
     - feuille 'Evaluation de la finalité' (au lieu de 'Alignement avec le besoin')
     - feuille 'Solutions' ou 'Solution'
    Retourne : df_comp, df_ent, df_align, df_sol
    """
    xls = pd.ExcelFile(file, engine="openpyxl")
    available_sheets = [sheet.strip() for sheet in xls.sheet_names]

    # --- 1) Analyse comparative (anciennement 'Comparatif') ---
    sheet_comp = None
    for name in ["Analyse comparative", "Comparatif"]:
        if name in available_sheets:
            sheet_comp = name
            break
    if sheet_comp is None:
        raise ValueError(f"Feuille 'Analyse comparative' ou 'Comparatif' introuvable. Feuilles disponibles : {available_sheets}")
    df_comp = pd.read_excel(xls, sheet_name=sheet_comp, engine="openpyxl")

    # --- 2) Entreprise(s) ---
    sheet_ent = None
    for name in ["Entreprises", "Entreprise"]:
        if name in available_sheets:
            sheet_ent = name
            break
    if sheet_ent is None:
        raise ValueError(f"Feuille 'Entreprise' ou 'Entreprises' introuvable. Feuilles disponibles : {available_sheets}")
    df_ent = pd.read_excel(xls, sheet_name=sheet_ent, engine="openpyxl")

    # --- 3) Alignement/Évaluation finale ---
    sheet_align = None
    for name in ["Evaluation de la finalité", "Alignement avec le besoin"]:
        if name in available_sheets:
            sheet_align = name
            break
    if sheet_align is None:
        raise ValueError(f"Feuille 'Evaluation de la finalité' ou 'Alignement avec le besoin' introuvable. Feuilles disponibles : {available_sheets}")
    df_align = pd.read_excel(xls, sheet_name=sheet_align, engine="openpyxl")

    # --- 4) Solutions ---
    sheet_sol = None
    for name in ["Solutions", "Solution"]:
        if name in available_sheets:
            sheet_sol = name
            break
    if sheet_sol is None:
        raise ValueError(f"Feuille 'Solutions' ou 'Solution' introuvable. Feuilles disponibles : {available_sheets}")
    df_sol = pd.read_excel(xls, sheet_name=sheet_sol, engine="openpyxl")

    # --- Nettoyage basique des colonnes ---
    df_comp.columns  = [str(col).strip() for col in df_comp.columns]
    df_ent.columns   = [str(col).strip() for col in df_ent.columns]
    df_align.columns = [str(col).strip() for col in df_align.columns]
    df_sol.columns   = [str(col).strip() for col in df_sol.columns]

    return df_comp, df_ent, df_align, df_sol