
# =================== VARIABLES GLOBALES (labels, chemins, colonnes, erreurs) ===================
TEMP_IMAGE_DIR = "/tmp/excel_images"
EXCEL_IMAGE_FILENAME = "image_{idx}_row_{row}.png"
SHEET_COMP_NAMES = ["Analyse comparative", "Comparatif"]
SHEET_ENT_NAMES = ["Entreprises", "Entreprise"]
SHEET_ALIGN_NAMES = ["Evaluation de la finalité", "Alignement avec le besoin"]
SHEET_SOL_NAMES = ["Solutions", "Solution"]
ERROR_SHEET_COMP = "Feuille 'Analyse comparative' ou 'Comparatif' introuvable. Feuilles disponibles : {available_sheets}"
ERROR_SHEET_ENT = "Feuille 'Entreprise' ou 'Entreprises' introuvable. Feuilles disponibles : {available_sheets}"
ERROR_SHEET_ALIGN = "Feuille 'Evaluation de la finalité' ou 'Alignement avec le besoin' introuvable. Feuilles disponibles : {available_sheets}"
ERROR_SHEET_SOL = "Feuille 'Solutions' ou 'Solution' introuvable. Feuilles disponibles : {available_sheets}"
CLEAN_COL_LOGO = "Logo"
EXCEL_ERRORS = ['#VALUE!', '#NAME?', '#REF!', '#DIV/0!', '#NUM!', '#NULL!']

import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image
import io
import os

def _find_sheet(available_sheets, possible_names, error_message):
    for name in possible_names:
        if name in available_sheets:
            return name
    raise ValueError(error_message.format(available_sheets=available_sheets))

def _extract_image_info(image, idx, temp_dir):
    # Déterminer la position de l'image
    row_index = 1  # par défaut
    col_index = 0  # par défaut
    if hasattr(image, 'anchor'):
        if hasattr(image.anchor, 'row'):
            row_index = image.anchor.row - 1  # Excel est 1-indexé, Python 0-indexé
            col_index = getattr(image.anchor, 'col', 1) - 1
        elif hasattr(image.anchor, '_from'):
            from_info = image.anchor._from
            if hasattr(from_info, 'row'):
                row_index = from_info.row
            if hasattr(from_info, 'col'):
                col_index = from_info.col
    print(f"Image {idx+1} trouvée à la ligne {row_index + 1}, colonne {col_index + 1}")
    temp_filename = f"{temp_dir}/" + EXCEL_IMAGE_FILENAME.format(idx=idx+1, row=row_index+1)
    image_bytes = io.BytesIO()
    image.ref.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    with open(temp_filename, 'wb') as f:
        f.write(image_bytes.getvalue())
    print(f"Image extraite et sauvegardée: {temp_filename}")
    return row_index, image_bytes.getvalue()

def extract_images_from_excel(file, sheet_name):
    """
    Extrait TOUTES les images de la feuille Excel et les sauvegarde temporairement.
    Les images sont associées aux lignes en fonction de leur position.
    """
    images_dict = {}
    def log_and_return(msg):
        print(msg)
        return images_dict
    try:
        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
        workbook = openpyxl.load_workbook(file, data_only=False)
        if sheet_name not in workbook.sheetnames:
            return log_and_return(f"Feuille {sheet_name} non trouvée")
        worksheet = workbook[sheet_name]
        # Vérification robuste de la présence d'images
        images = getattr(worksheet, 'images', None)
        if images is None:
            print("Aucune image trouvée dans la feuille (attribut 'images' absent ou None).")
            workbook.close()
            return images_dict
        print(f"Nombre total d'images dans la feuille : {len(images)}")
        for idx, image in enumerate(images):
            try:
                row_index, image_bytes = _extract_image_info(image, idx, TEMP_IMAGE_DIR)
                images_dict[row_index] = image_bytes
            except Exception as e:
                print(f"Erreur lors de l'extraction de l'image {idx+1}: {e}")
        print(f"Total d'images extraites : {len(images_dict)}")
        workbook.close()
    except Exception as e:
        print(f"Erreur lors de l'extraction des images : {e}")
        import traceback
        traceback.print_exc()
    return images_dict

def load_data(file):
    """
    Charge les quatre DataFrames principaux depuis le fichier Excel :
     - feuille 'Analyse comparative' (ou 'Comparatif')
     - feuille 'Entreprise' ou 'Entreprises'
     - feuille 'Evaluation de la finalité' (ou 'Alignement avec le besoin')
     - feuille 'Solutions' ou 'Solution'
    Retourne : df_comp, df_ent, df_align, df_sol
    """
    xls = pd.ExcelFile(file, engine="openpyxl")
    available_sheets = [str(sheet).strip() for sheet in xls.sheet_names]
    sheet_comp = _find_sheet(available_sheets, SHEET_COMP_NAMES, ERROR_SHEET_COMP)
    df_comp = pd.read_excel(xls, sheet_name=sheet_comp, engine="openpyxl")
    sheet_ent = _find_sheet(available_sheets, SHEET_ENT_NAMES, ERROR_SHEET_ENT)
    df_ent = pd.read_excel(xls, sheet_name=sheet_ent, engine="openpyxl")
    # Chargement optionnel de la feuille d'alignement
    sheet_align = None
    df_align = None
    for name in SHEET_ALIGN_NAMES:
        if name in available_sheets:
            sheet_align = name
            df_align = pd.read_excel(xls, sheet_name=sheet_align, engine="openpyxl")
            break
    if df_align is None:
        print(f"Aucune feuille d'alignement trouvée. Feuilles attendues : {SHEET_ALIGN_NAMES}. Feuilles disponibles : {available_sheets}")
    sheet_sol = _find_sheet(available_sheets, SHEET_SOL_NAMES, ERROR_SHEET_SOL)
    df_sol = pd.read_excel(xls, sheet_name=sheet_sol, engine="openpyxl")
    # --- Nettoyage basique des colonnes ---
    df_comp.columns  = [str(col).strip() for col in df_comp.columns]
    df_ent.columns   = [str(col).strip() for col in df_ent.columns]
    if df_align is not None:
        df_align.columns = [str(col).strip() for col in df_align.columns]
    df_sol.columns   = [str(col).strip() for col in df_sol.columns]
    # --- Nettoyage des erreurs Excel dans la colonne Logo ---
    if CLEAN_COL_LOGO in df_ent.columns:
        print("Nettoyage de la colonne Logo...")
        logo_cleaned = 0
        for i in range(len(df_ent)):
            current_value = df_ent.iloc[i, df_ent.columns.get_loc(CLEAN_COL_LOGO)]
            if isinstance(current_value, str) and current_value.strip() in EXCEL_ERRORS:
                df_ent.at[i, CLEAN_COL_LOGO] = None
                logo_cleaned += 1
                print(f"Ligne {i+1}: Erreur Excel '{current_value}' nettoyée")
        print(f"Total de {logo_cleaned} erreurs Excel nettoyées dans la colonne Logo")
    return df_comp, df_ent, df_align, df_sol