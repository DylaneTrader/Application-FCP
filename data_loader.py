"""
Legacy data loader - Conservé pour référence historique
Pour le chargement de données, utiliser utils.py à la place

Ce fichier contient le code original pour télécharger les données depuis SharePoint.
Note: Ce code nécessite un accès direct à SharePoint et n'est plus utilisé activement.
"""

import pandas as pd

# URL SharePoint (lien de téléchargement direct)
url = "https://boursecgf.sharepoint.com/:x:/r/sites/CGF_GESTION/_layouts/15/Doc.aspx?sourcedoc=%7BBB0CA8B9-241C-42A5-95FE-B52CA4DFC9B7%7D&file=MY%20PTF%20OPCVM.xlsm&action=default&mobileredirect=true"

def download_from_sharepoint():
    """
    Fonction legacy pour télécharger les données depuis SharePoint
    
    Note: Cette fonction nécessite des droits d'accès SharePoint appropriés
    et n'est plus utilisée dans l'application actuelle.
    """
    # Lecture du fichier
    data_vl = pd.read_excel(
        url,
        sheet_name="Cours",
    )

    data_vl = data_vl.drop([0, 1]).reset_index(drop=True)
    data_vl = data_vl.drop(columns=data_vl.columns[0])
    data_vl = data_vl.rename(columns={"TITRE": "Date"})
    data_vl["Date"] = pd.to_datetime(data_vl["Date"], format="%d/%m/%Y")
    for col in data_vl.columns[1:]:
        data_vl[col] = pd.to_numeric(data_vl[col], errors='coerce')

    data_vl.to_csv("data/data_vl.csv", index=False)
    return data_vl
