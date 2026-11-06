"""Simulateur de placement (repris du dépôt Simulateur-d-investissement).

On fixe trois des quatre grandeurs (capital initial, versement mensuel, durée, valeur finale) et on calcule
la quatrième. Le taux est un rendement annuel effectif, comme ceux des fonds : il est converti en taux
mensuel équivalent (1 + t)^(1/12) − 1. Les versements sont faits en fin de mois.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

MOIS_MAX = 1200  # 100 ans

CALCULS = {
    "valeur_finale": "Valeur finale",
    "versement": "Versement mensuel",
    "capital_initial": "Capital initial",
    "duree": "Durée",
}


class ErreurSimulation(ValueError):
    pass


def taux_mensuel(taux_annuel: float) -> float:
    if taux_annuel <= -1:
        raise ErreurSimulation("Le rendement annuel doit être supérieur à −100 %.")
    return (1 + taux_annuel) ** (1 / 12) - 1


def _facteurs(taux_annuel: float, mois: int) -> tuple[float, float]:
    """(capitalisation du capital, valeur finale d'un versement de 1 par mois) sur ``mois`` mois."""
    r = taux_mensuel(taux_annuel)
    croissance = (1 + r) ** mois
    rente = mois if r == 0 else (croissance - 1) / r
    return croissance, rente


def _verifier(capital: float = 0, versement: float = 0, annees: float = 0):
    if capital < 0 or versement < 0:
        raise ErreurSimulation("Les montants ne peuvent pas être négatifs.")
    if not 0 <= annees <= 100:
        raise ErreurSimulation("La durée doit être comprise entre 0 et 100 ans.")


def valeur_finale(capital: float, versement: float, taux_annuel: float, annees: float) -> float:
    _verifier(capital, versement, annees)
    croissance, rente = _facteurs(taux_annuel, round(annees * 12))
    return capital * croissance + versement * rente


def versement_necessaire(objectif: float, capital: float, taux_annuel: float, annees: float) -> float:
    _verifier(capital, 0, annees)
    mois = round(annees * 12)
    if mois == 0:
        raise ErreurSimulation("La durée doit être d'au moins un mois.")
    croissance, rente = _facteurs(taux_annuel, mois)
    return max((objectif - capital * croissance) / rente, 0.0)


def capital_necessaire(objectif: float, versement: float, taux_annuel: float, annees: float) -> float:
    _verifier(0, versement, annees)
    croissance, rente = _facteurs(taux_annuel, round(annees * 12))
    return max((objectif - versement * rente) / croissance, 0.0)


def duree_necessaire(objectif: float, capital: float, versement: float, taux_annuel: float) -> int | None:
    """Nombre de mois pour atteindre l'objectif, ou None au-delà de 100 ans."""
    _verifier(capital, versement)
    if objectif <= capital:
        return 0
    r = taux_mensuel(taux_annuel)
    if r > 0:
        numerateur = objectif * r + versement
        denominateur = capital * r + versement
        if denominateur <= 0:
            return None
        mois = math.ceil(math.log(numerateur / denominateur) / math.log(1 + r) - 1e-9)
        return mois if mois <= MOIS_MAX else None
    valeur = capital
    for mois in range(1, MOIS_MAX + 1):
        valeur = valeur * (1 + r) + versement
        if valeur >= objectif:
            return mois
    return None


def echeancier(capital: float, versement: float, taux_annuel: float, mois: int) -> pd.DataFrame:
    """Évolution mois par mois : montant investi, valeur, intérêts cumulés."""
    r = taux_mensuel(taux_annuel)
    lignes, valeur = [], capital
    for k in range(mois + 1):
        if k:
            valeur = valeur * (1 + r) + versement
        investi = capital + versement * k
        lignes.append({"mois": k, "annee": k / 12, "investi": investi, "valeur": valeur, "interets": valeur - investi})
    return pd.DataFrame(lignes)


def annuel(tableau: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par fin d'année (et la dernière ligne si la durée n'est pas un nombre entier d'années)."""
    garde = (tableau["mois"] % 12 == 0) & (tableau["mois"] > 0)
    garde.iloc[-1] = True
    return tableau[garde]


@dataclass
class Resultat:
    calcul: str
    capital: float
    versement: float
    taux: float
    mois: int | None
    objectif: float | None
    valeur: float | None
    tableau: pd.DataFrame | None


def resoudre(calcul: str, *, capital: float = 0, versement: float = 0, taux: float = 0.05, annees: float = 10,
             objectif: float = 0) -> Resultat:
    """Calcule la grandeur ``calcul`` et l'échéancier qui en résulte."""
    if calcul not in CALCULS:
        raise ErreurSimulation(f"Calcul inconnu : {calcul}")
    _verifier(capital, versement, annees)
    if calcul != "valeur_finale" and objectif <= 0:
        raise ErreurSimulation("Indiquez un objectif positif.")
    mois = round(annees * 12)
    if calcul == "valeur_finale":
        objectif = None
    elif calcul == "versement":
        versement = versement_necessaire(objectif, capital, taux, annees)
    elif calcul == "capital_initial":
        capital = capital_necessaire(objectif, versement, taux, annees)
    else:
        mois = duree_necessaire(objectif, capital, versement, taux)
        if mois is None:
            return Resultat(calcul, capital, versement, taux, None, objectif, None, None)
    tableau = echeancier(capital, versement, taux, mois)
    return Resultat(calcul, capital, versement, taux, mois, objectif, float(tableau["valeur"].iloc[-1]), tableau)


def retraits(capital: float, versement: float, taux_annuel: float, annees_epargne: float, retrait: float,
             annees_retrait: float) -> tuple[pd.DataFrame, float, int | None]:
    """Épargne puis retraits mensuels. Renvoie l'évolution, le capital constitué et le mois d'épuisement."""
    r = taux_mensuel(taux_annuel)
    lignes, valeur, epuise = [], capital, None
    m1, m2 = round(annees_epargne * 12), round(annees_retrait * 12)
    for k in range(1, m1 + m2 + 1):
        if k <= m1:
            valeur = valeur * (1 + r) + versement
            phase = "Épargne"
        else:
            valeur = valeur * (1 + r) - retrait
            phase = "Retraits"
            if valeur <= 0:
                valeur = 0.0
                epuise = epuise or k
        lignes.append({"mois": k, "annee": k / 12, "valeur": valeur, "phase": phase})
    constitue = lignes[m1 - 1]["valeur"] if m1 else capital
    return pd.DataFrame(lignes), constitue, epuise


def retrait_soutenable(capital: float, taux_annuel: float, annees: float) -> float:
    """Retrait mensuel constant qui épuise exactement le capital en ``annees`` ans."""
    mois = round(annees * 12)
    if mois <= 0:
        return 0.0
    r = taux_mensuel(taux_annuel)
    return capital / mois if r == 0 else capital * r / (1 - (1 + r) ** -mois)


def valeur_reelle(tableau: pd.DataFrame, inflation: float) -> pd.Series:
    """Valeur exprimée en pouvoir d'achat d'aujourd'hui."""
    return tableau["valeur"] / (1 + inflation) ** tableau["annee"]
