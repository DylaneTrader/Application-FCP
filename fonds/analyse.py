"""Calculs sur une série de valeurs liquidatives (pandas pur, sans base de données).

Les VL d'un FCP peuvent être quotidiennes ou hebdomadaires : la fréquence d'annualisation est déduite du
nombre d'observations par an, pas supposée.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

JOURS_AN = 365.25


def periodes_par_an(vl: pd.Series) -> float:
    """Nombre moyen d'observations par an (≈ 252 en quotidien ouvré, ≈ 52 en hebdomadaire)."""
    if len(vl) < 2:
        return np.nan
    jours = (vl.index[-1] - vl.index[0]).days
    return (len(vl) - 1) / (jours / JOURS_AN) if jours > 0 else np.nan


def taux_annuel(v0: float, v1: float, jours: float) -> float:
    if jours <= 0 or v0 <= 0:
        return np.nan
    return (v1 / v0) ** (JOURS_AN / jours) - 1


def cagr(vl: pd.Series) -> float:
    if len(vl) < 2:
        return np.nan
    return taux_annuel(vl.iloc[0], vl.iloc[-1], (vl.index[-1] - vl.index[0]).days)


def _valeur_au(vl: pd.Series, date: pd.Timestamp) -> tuple[pd.Timestamp, float] | None:
    """Dernière VL publiée au plus tard à ``date``."""
    avant = vl.loc[:date]
    return None if avant.empty else (avant.index[-1], float(avant.iloc[-1]))


def performances(vl: pd.Series) -> list[dict]:
    """Rendements cumulés (et annualisés au-delà d'un an) aux horizons usuels, à la dernière VL."""
    if len(vl) < 2:
        return []
    fin, v = vl.index[-1], float(vl.iloc[-1])
    horizons = [("1 mois", pd.DateOffset(months=1)), ("3 mois", pd.DateOffset(months=3)),
                ("6 mois", pd.DateOffset(months=6)), ("Depuis le 1er janvier", None),
                ("1 an", pd.DateOffset(years=1)), ("3 ans", pd.DateOffset(years=3)),
                ("5 ans", pd.DateOffset(years=5))]
    lignes = []
    for nom, decalage in horizons:
        cible = pd.Timestamp(fin.year - 1, 12, 31) if decalage is None else fin - decalage
        if cible < vl.index[0]:
            lignes.append({"periode": nom, "cumule": None, "annualise": None})
            continue
        date0, v0 = _valeur_au(vl, cible)
        jours = (fin - date0).days
        lignes.append({"periode": nom, "cumule": v / v0 - 1,
                       "annualise": taux_annuel(v0, v, jours) if jours >= 365 else None})
    jours = (fin - vl.index[0]).days
    lignes.append({"periode": f"Depuis le {vl.index[0]:%d/%m/%Y}", "cumule": v / vl.iloc[0] - 1,
                   "annualise": taux_annuel(vl.iloc[0], v, jours) if jours >= 365 else None})
    return lignes


def calendrier(vl: pd.Series) -> list[dict]:
    """Rendement de chaque année civile ; la première année est partielle si elle ne part pas du 31/12."""
    lignes = []
    for annee in sorted(set(vl.index.year)):
        de_lannee = vl[vl.index.year == annee]
        avant = vl[vl.index.year < annee]
        depart = float(avant.iloc[-1]) if len(avant) else float(de_lannee.iloc[0])
        lignes.append({"annee": annee, "rendement": float(de_lannee.iloc[-1]) / depart - 1,
                       "partiel": avant.empty or annee == vl.index[-1].year})
    return lignes


def drawdowns(vl: pd.Series) -> pd.Series:
    return vl / vl.cummax() - 1


def indicateurs_risque(vl: pd.Series, taux_sans_risque: float) -> dict:
    r = vl.pct_change().dropna()
    if len(r) < 5:
        return {}
    ppa = periodes_par_an(vl)
    vol = r.std() * np.sqrt(ppa)
    deficit = np.sqrt((np.minimum(r, 0) ** 2).mean()) * np.sqrt(ppa)
    taux = cagr(vl)
    dd = drawdowns(vl)
    return {
        "Rendement annualisé": taux,
        "Volatilité annualisée": vol,
        "Ratio de Sharpe": (taux - taux_sans_risque) / vol if vol > 0 else np.nan,
        "Ratio de Sortino": (taux - taux_sans_risque) / deficit if deficit > 0 else np.nan,
        "Perte maximale (drawdown)": float(dd.min()),
        "Date du creux": dd.idxmin(),
        "VaR historique 95 % (par période)": float(-r.quantile(0.05)),
        "Périodes en hausse": float((r > 0).mean()),
        "Fréquence des VL": "quotidienne" if ppa > 150 else "hebdomadaire" if ppa > 30 else "mensuelle ou moins",
    }


def rendements_glissants(vl: pd.Series, annees: int = 1) -> pd.Series:
    """Rendement sur ``annees`` an(s) se terminant à chaque date (dès qu'assez d'historique)."""
    dates = vl.index
    cibles = dates - pd.DateOffset(years=annees)
    pos = dates.searchsorted(cibles, side="right") - 1
    ok = pos >= 0
    debut = vl.to_numpy()[pos[ok]]
    return pd.Series(vl.to_numpy()[ok] / debut - 1, index=dates[ok])


def rendement_attendu(vl: pd.Series, annees: int | None = None) -> dict | None:
    """Estimation du rendement attendu à partir de l'historique des VL (``annees`` dernières années).

    Le rendement logarithmique moyen μ et la volatilité σ sont annualisés. Le taux médian exp(μ) − 1 est
    le rendement composé historique : la moitié des trajectoires simulées font mieux. Le taux moyen
    exp(μ + σ²/2) − 1 est l'espérance d'un an de placement ; il dépasse la médiane, d'autant plus que le
    fonds est volatil. Rien ne garantit qu'un rendement passé se reproduise.
    """
    if annees:
        vl = vl[vl.index >= vl.index[-1] - pd.DateOffset(years=annees)]
    if len(vl) < 10 or (vl.index[-1] - vl.index[0]).days < 180:
        return None
    log_r = np.log(vl).diff().dropna()
    ppa = periodes_par_an(vl)
    mu, sigma = float(log_r.mean() * ppa), float(log_r.std() * np.sqrt(ppa))
    estimation = {"mu": mu, "sigma": sigma, "debut": vl.index[0], "fin": vl.index[-1], "observations": len(vl),
                  "taux_median": float(np.exp(mu) - 1), "taux_moyen": float(np.exp(mu + sigma ** 2 / 2) - 1),
                  "glissant": None}
    g = rendements_glissants(vl, 1)
    if len(g) >= 10:
        estimation["glissant"] = {"nombre": len(g), "median": float(g.median()), "p10": float(g.quantile(0.10)),
                                  "p90": float(g.quantile(0.90)), "part_negatifs": float((g < 0).mean()),
                                  "pire": float(g.min()), "meilleur": float(g.max())}
    return estimation


QUANTILES = (0.05, 0.25, 0.5, 0.75, 0.95)


def projection(mu: float, sigma: float, annees: int, capital: float, versement: float = 0.0,
               objectif: float | None = None, trajectoires: int = 4000, graine: int = 0) -> dict:
    """Valeur du placement mois par mois sous un modèle lognormal (μ, σ annuels), versements en fin de mois.

    Renvoie les quantiles 5/25/50/75/95 % à chaque mois, le montant investi et, à l'échéance, la probabilité
    de finir sous le montant investi (et d'atteindre ``objectif`` s'il est donné).
    """
    mois = int(round(annees * 12))
    rng = np.random.default_rng(graine)
    croissance = np.exp(mu / 12 + sigma / np.sqrt(12) * rng.standard_normal((trajectoires, mois)))
    valeurs = np.empty((trajectoires, mois + 1))
    valeurs[:, 0] = capital
    for k in range(mois):
        valeurs[:, k + 1] = valeurs[:, k] * croissance[:, k] + versement
    q = np.quantile(valeurs, QUANTILES, axis=0)
    investi = capital + versement * np.arange(mois + 1)
    tableau = pd.DataFrame({f"q{int(p * 100):02d}": q[i] for i, p in enumerate(QUANTILES)})
    tableau.insert(0, "annee", np.arange(mois + 1) / 12)
    tableau["investi"] = investi
    finales = valeurs[:, -1]
    return {"tableau": tableau, "investi": float(investi[-1]),
            "probabilite_perte": float((finales < investi[-1]).mean()),
            "probabilite_objectif": float((finales >= objectif).mean()) if objectif else None,
            "finales": {f"q{int(p * 100):02d}": float(q[i, -1]) for i, p in enumerate(QUANTILES)}}
