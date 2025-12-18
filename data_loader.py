import pandas as pd

# (lien de téléchargement direct)
url = "https://boursecgf.sharepoint.com/:x:/r/sites/CGF_GESTION/_layouts/15/Doc.aspx?sourcedoc=%7BBB0CA8B9-241C-42A5-95FE-B52CA4DFC9B7%7D&file=MY%20PTF%20OPCVM.xlsm&action=default&mobileredirect=true"

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