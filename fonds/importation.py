"""Import d'un classeur Excel de SGO : VL et actifs nets en colonnes (une par fonds), flux en lignes.

Format attendu (celui de data_fcp.xlsx) :
- feuille « Valeurs Liquidatives » : Date, puis une colonne par fonds ;
- feuille « Actifs Nets » : idem ;
- feuille « Souscriptions Rachats » : Date, Type de clients, Opérations (Souscriptions / Rachats), FCP, Montant.
Chaque feuille est facultative. Un nom de fonds est rapproché du nom ou des alias d'un fonds existant de la
SGO (sans tenir compte de la casse, des tirets ni des espaces) ; sinon le fonds est créé.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import donnees
from .models import SGO, Fonds

FEUILLE_VL = "Valeurs Liquidatives"
FEUILLE_ACTIFS = "Actifs Nets"
FEUILLE_FLUX = "Souscriptions Rachats"


def normaliser(nom: str) -> str:
    nom = unicodedata.normalize("NFKD", str(nom)).encode("ascii", "ignore").decode()
    return re.sub(r"[\s\-_']+", " ", nom).strip().upper()


def categorie_probable(nom: str) -> str:
    n = normaliser(nom)
    for motif, categorie in (("FCPE", "fcpe"), ("FCPR", "fcpr"), ("MONETAIRE", "monetaire"), ("LIQUIDITE", "monetaire"),
                             ("ACTION", "actions"), ("OBLIGATAIRE", "obligataire"), ("RENTE", "obligataire")):
        if motif in n.split() or n.startswith(motif):
            return categorie
    return Fonds.Categorie.AUTRE


@dataclass
class Rapport:
    vl: int = 0
    actifs: int = 0
    flux: int = 0
    fonds_crees: list[str] = field(default_factory=list)
    ignores: list[str] = field(default_factory=list)
    par_feuille: dict[str, set[str]] = field(default_factory=dict)

    def fonds_isoles(self) -> dict[str, list[str]]:
        """Fonds présents dans une seule feuille de VL ou d'actifs : candidats à un alias."""
        vl, actifs = self.par_feuille.get(FEUILLE_VL, set()), self.par_feuille.get(FEUILLE_ACTIFS, set())
        if not vl or not actifs:
            return {}
        return {"VL sans actifs nets": sorted(vl - actifs), "Actifs nets sans VL": sorted(actifs - vl)}


class Rapprocheur:
    def __init__(self, sgo: SGO, rapport: Rapport):
        self.sgo, self.rapport = sgo, rapport
        self.index = {}
        for f in sgo.fonds.all():
            for n in f.noms_connus():
                self.index[normaliser(n)] = f

    def fonds(self, nom: str) -> Fonds:
        cle = normaliser(nom)
        if cle not in self.index:
            f = Fonds.objects.create(sgo=self.sgo, nom=str(nom).strip(), categorie=categorie_probable(nom))
            self.index[cle] = f
            self.rapport.fonds_crees.append(f.nom)
        return self.index[cle]


def _dates(colonne: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(colonne):
        return colonne
    return pd.to_datetime(colonne, dayfirst=True, errors="coerce")


def _large(df: pd.DataFrame, rapprocheur: Rapprocheur, ecrire, feuille: str, rapport: Rapport) -> int:
    df = df.rename(columns={df.columns[0]: "Date"})
    df["Date"] = _dates(df["Date"])
    df = df.dropna(subset=["Date"])
    total, vus = 0, set()
    for colonne in df.columns[1:]:
        if str(colonne).startswith("Unnamed"):
            continue
        valeurs = pd.to_numeric(df[colonne], errors="coerce")
        garde = valeurs.notna() & (valeurs > 0)
        if not garde.any():
            rapport.ignores.append(f"{feuille} : « {colonne} » sans valeur exploitable")
            continue
        f = rapprocheur.fonds(colonne)
        vus.add(f.nom)
        points = list(zip(df.loc[garde, "Date"].dt.date, valeurs[garde]))
        total += ecrire(f, points)
    rapport.par_feuille[feuille] = vus
    return total


def _flux(df: pd.DataFrame, rapprocheur: Rapprocheur) -> int:
    colonnes = {normaliser(c): c for c in df.columns}
    try:
        c_date, c_type, c_op, c_fonds, c_montant = (colonnes[k] for k in
                                                    ("DATE", "TYPE DE CLIENTS", "OPERATIONS", "FCP", "MONTANT"))
    except KeyError as manque:
        raise ValueError(f"Feuille {FEUILLE_FLUX} : colonne manquante {manque}") from None
    df = df.assign(_date=_dates(df[c_date]), _montant=pd.to_numeric(df[c_montant], errors="coerce"))
    df = df.dropna(subset=["_date", "_montant", c_fonds])
    df["_sens"] = df[c_op].map(lambda o: "R" if normaliser(o).startswith("RACHAT") else
                               "S" if normaliser(o).startswith("SOUSCRIPTION") else None)
    df = df.dropna(subset=["_sens"])
    total = 0
    for nom, groupe in df.groupby(c_fonds):
        lignes = [{"date": d.date(), "sens": s, "type_client": str(t or "")[:80], "montant": abs(float(m))}
                  for d, s, t, m in zip(groupe["_date"], groupe["_sens"], groupe[c_type], groupe["_montant"])]
        total += donnees.remplacer_flux(rapprocheur.fonds(nom), lignes)
    return total


def importer_classeur(chemin: str | Path, sgo: SGO) -> Rapport:
    rapport = Rapport()
    rapprocheur = Rapprocheur(sgo, rapport)
    chemin = Path(chemin)
    if chemin.suffix.lower() == ".csv":
        rapport.vl = _large(pd.read_csv(chemin, sep=None, engine="python"), rapprocheur, donnees.enregistrer_vl,
                            FEUILLE_VL, rapport)
        return rapport
    with pd.ExcelFile(chemin) as classeur:
        feuilles = {normaliser(f): f for f in classeur.sheet_names}
        lues = {cle: pd.read_excel(classeur, sheet_name=feuilles[normaliser(cle)])
                for cle in (FEUILLE_VL, FEUILLE_ACTIFS, FEUILLE_FLUX) if normaliser(cle) in feuilles}
    if FEUILLE_VL in lues:
        rapport.vl = _large(lues[FEUILLE_VL], rapprocheur, donnees.enregistrer_vl, FEUILLE_VL, rapport)
    if FEUILLE_ACTIFS in lues:
        rapport.actifs = _large(lues[FEUILLE_ACTIFS], rapprocheur, donnees.enregistrer_actifs, FEUILLE_ACTIFS, rapport)
    if FEUILLE_FLUX in lues:
        rapport.flux = _flux(lues[FEUILLE_FLUX], rapprocheur)
    if not lues:
        raise ValueError(f"Aucune feuille reconnue dans {chemin.name} : {', '.join(feuilles.values())}")
    return rapport
