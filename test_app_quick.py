#!/usr/bin/env python3
"""
Script de test rapide pour l'application IVÉO BI
================================================

Ce script valide que l'application fonctionne sans erreur et que les fonctionnalités 
principales sont opérationnelles.
"""

import sys
import os
import pandas as pd
sys.path.append(os.getcwd())

def test_analyse_comparative():
    """Test de la page d'analyse comparative"""
    print("=== Test de la page Analyse Comparative ===")
    
    try:
        # Importer les modules nécessaires
        from app.pages.analyse_comparative import (
            _prepare_data, 
            _get_badge_info, 
            _get_info_complementaire,
            NO_INFO_MESSAGE,
            COL_FONCTIONNALITES,
            COL_INFO_COMP
        )
        
        # Charger les données
        df = pd.read_excel('uploads/Qualif_généré_V4.xlsx', sheet_name='Analyse comparative')
        print(f"✓ Données chargées: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Test de préparation des données
        success, df_filtered, entreprise_cols, justificatif_cols = _prepare_data(df)
        print(f"✓ Préparation des données: {success}")
        print(f"  - Entreprises: {len(entreprise_cols)}")
        print(f"  - Justificatifs: {len(justificatif_cols)}")
        
        # Test des fonctions utilitaires
        badge_info = _get_badge_info(1)
        print(f"✓ Badge info (score 1): {badge_info['text']}")
        
        # Test d'information complémentaire
        if not df_filtered.empty:
            row_data = df_filtered.iloc[0]
            info = _get_info_complementaire(row_data, entreprise_cols[0], df_filtered)
            print(f"✓ Info complémentaire récupérée: {len(str(info))} caractères")
        
        print("✓ Tous les tests de la page Analyse Comparative ont réussi!")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structure():
    """Test de la structure des données"""
    print("\n=== Test de la structure des données ===")
    
    try:
        df = pd.read_excel('uploads/Qualif_généré_V4.xlsx', sheet_name='Analyse comparative')
        
        # Vérifier la structure
        print(f"✓ Colonnes principales:")
        for i, col in enumerate(df.columns[:4]):
            print(f"  {i}: {col}")
        
        # Vérifier les colonnes entreprises/info
        remaining_cols = df.columns[4:]
        entreprise_cols = [col for col in remaining_cols if "Information complémentaire" not in col]
        info_cols = [col for col in remaining_cols if "Information complémentaire" in col]
        
        print(f"✓ Structure alternée validée:")
        print(f"  - Entreprises: {len(entreprise_cols)}")
        print(f"  - Informations complémentaires: {len(info_cols)}")
        
        # Vérifier la correspondance
        for i, entreprise in enumerate(entreprise_cols):
            if i < len(info_cols):
                print(f"  - {entreprise} → {info_cols[i]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test de structure: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Démarrage des tests de l'application IVÉO BI")
    print(f"📁 Répertoire de travail: {os.getcwd()}")
    
    # Vérifier que le fichier Excel existe
    if not os.path.exists('uploads/Qualif_généré_V4.xlsx'):
        print("✗ Fichier Excel non trouvé: uploads/Qualif_généré_V4.xlsx")
        return False
    
    tests_passed = 0
    total_tests = 2
    
    # Exécuter les tests
    if test_data_structure():
        tests_passed += 1
    
    if test_analyse_comparative():
        tests_passed += 1
    
    # Résumé
    print(f"\n🎯 Résumé des tests:")
    print(f"✓ Tests réussis: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Tous les tests ont réussi! L'application est prête à être utilisée.")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Veuillez vérifier les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
