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

def extract_images_from_excel(file, sheet_name, logo_column_name="Logo"):
    """
    Extrait TOUTES les images de la feuille Excel et les sauvegarde temporairement.
    Les images sont associées aux lignes en fonction de leur position.
    """
    images_dict = {}
    temp_dir = "/tmp/excel_images"
    
    try:
        # Créer le dossier temporaire
        os.makedirs(temp_dir, exist_ok=True)
        
        # Ouvrir le fichier Excel avec openpyxl AVANT le traitement pandas
        workbook = openpyxl.load_workbook(file, data_only=False)
        
        # Trouver la feuille
        if sheet_name not in workbook.sheetnames:
            print(f"Feuille {sheet_name} non trouvée")
            return images_dict
        
        worksheet = workbook[sheet_name]
        
        print(f"Nombre total d'images dans la feuille : {len(worksheet._images)}")
        
        # Extraire TOUTES les images de la feuille
        for idx, image in enumerate(worksheet._images):
            try:
                # Déterminer la position de l'image
                row_index = 1  # par défaut
                col_index = 0  # par défaut
                
                if hasattr(image, 'anchor'):
                    if hasattr(image.anchor, 'row'):
                        row_index = image.anchor.row - 1  # Excel est 1-indexé, Python 0-indexé
                        col_index = getattr(image.anchor, 'col', 1) - 1
                    elif hasattr(image.anchor, '_from'):
                        # Pour certains types d'anchors
                        from_info = image.anchor._from
                        if hasattr(from_info, 'row'):
                            row_index = from_info.row
                        if hasattr(from_info, 'col'):
                            col_index = from_info.col
                
                print(f"Image {idx+1} trouvée à la ligne {row_index + 1}, colonne {col_index + 1}")
                
                # Sauvegarder l'image temporairement
                temp_filename = f"{temp_dir}/image_{idx+1}_row_{row_index + 1}.png"
                
                # Extraire l'image
                image_bytes = io.BytesIO()
                image.ref.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                
                # Sauvegarder en tant que fichier temporaire
                with open(temp_filename, 'wb') as f:
                    f.write(image_bytes.getvalue())
                
                # Stocker les bytes dans le dictionnaire
                images_dict[row_index] = image_bytes.getvalue()
                print(f"Image extraite et sauvegardée: {temp_filename}")
                
            except Exception as e:
                print(f"Erreur lors de l'extraction de l'image {idx+1}: {e}")
                continue
        
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
     - feuille 'Analyse comparative' (au lieu de 'Comparatif')
     - feuille 'Entreprise' ou 'Entreprises'
     - feuille 'Evaluation de la finalité' (au lieu de 'Alignement avec le besoin')
     - feuille 'Solutions' ou 'Solution'
    Retourne : df_comp, df_ent, df_align, df_sol
    """
    
    xls = pd.ExcelFile(file, engine="openpyxl")
    available_sheets = [sheet.strip() for sheet in xls.sheet_names]

    sheet_comp = _find_sheet(
        available_sheets,
        ["Analyse comparative", "Comparatif"],
        "Feuille 'Analyse comparative' ou 'Comparatif' introuvable. Feuilles disponibles : {available_sheets}"
    )
    df_comp = pd.read_excel(xls, sheet_name=sheet_comp, engine="openpyxl")

    sheet_ent = _find_sheet(
        available_sheets,
        ["Entreprises", "Entreprise"],
        "Feuille 'Entreprise' ou 'Entreprises' introuvable. Feuilles disponibles : {available_sheets}"
    )
    df_ent = pd.read_excel(xls, sheet_name=sheet_ent, engine="openpyxl")

    sheet_align = _find_sheet(
        available_sheets,
        ["Evaluation de la finalité", "Alignement avec le besoin"],
        "Feuille 'Evaluation de la finalité' ou 'Alignement avec le besoin' introuvable. Feuilles disponibles : {available_sheets}"
    )
    df_align = pd.read_excel(xls, sheet_name=sheet_align, engine="openpyxl")

    sheet_sol = _find_sheet(
        available_sheets,
        ["Solutions", "Solution"],
        "Feuille 'Solutions' ou 'Solution' introuvable. Feuilles disponibles : {available_sheets}"
    )
    df_sol = pd.read_excel(xls, sheet_name=sheet_sol, engine="openpyxl")

    # --- Nettoyage basique des colonnes ---
    df_comp.columns  = [str(col).strip() for col in df_comp.columns]
    df_ent.columns   = [str(col).strip() for col in df_ent.columns]
    df_align.columns = [str(col).strip() for col in df_align.columns]
    df_sol.columns   = [str(col).strip() for col in df_sol.columns]

    # --- Nettoyage des erreurs Excel dans la colonne Logo ---
    if 'Logo' in df_ent.columns:
        print("Nettoyage de la colonne Logo...")
        logo_cleaned = 0
        for i in range(len(df_ent)):
            current_value = df_ent.iloc[i, df_ent.columns.get_loc('Logo')]
            if isinstance(current_value, str) and current_value.strip() in ['#VALUE!', '#NAME?', '#REF!', '#DIV/0!', '#NUM!', '#NULL!']:
                df_ent.iloc[i, df_ent.columns.get_loc('Logo')] = None
                logo_cleaned += 1
                print(f"Ligne {i+1}: Erreur Excel '{current_value}' nettoyée")
        print(f"Total de {logo_cleaned} erreurs Excel nettoyées dans la colonne Logo")

    return df_comp, df_ent, df_align, df_sol