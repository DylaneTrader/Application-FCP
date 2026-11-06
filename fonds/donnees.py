"""Passage de la base de données aux séries pandas, et écriture groupée (API, import)."""
from __future__ import annotations

import pandas as pd
from django.db import transaction

from .models import ActifNet, Flux, Fonds, ValeurLiquidative


def serie_vl(fonds: Fonds) -> pd.Series:
    lignes = list(fonds.vls.order_by("date").values_list("date", "valeur"))
    if not lignes:
        return pd.Series(dtype=float)
    dates, valeurs = zip(*lignes)
    return pd.Series(valeurs, index=pd.DatetimeIndex(dates), name=fonds.nom, dtype=float)


def serie_actifs(fonds: Fonds) -> pd.Series:
    lignes = list(fonds.actifs_nets.order_by("date").values_list("date", "montant"))
    if not lignes:
        return pd.Series(dtype=float)
    dates, montants = zip(*lignes)
    return pd.Series(montants, index=pd.DatetimeIndex(dates), name=fonds.nom, dtype=float)


def actifs_sgo(sgo) -> pd.DataFrame:
    """Actifs nets de tous les fonds de la SGO, une colonne par fonds."""
    lignes = ActifNet.objects.filter(fonds__sgo=sgo).values_list("date", "fonds__nom", "montant")
    df = pd.DataFrame(list(lignes), columns=["date", "fonds", "montant"])
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.pivot_table(index="date", columns="fonds", values="montant", aggfunc="last").sort_index()


def flux_sgo(sgo) -> pd.DataFrame:
    lignes = Flux.objects.filter(fonds__sgo=sgo).values_list("date", "fonds__nom", "sens", "type_client", "montant")
    df = pd.DataFrame(list(lignes), columns=["date", "fonds", "sens", "type_client", "montant"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def enregistrer_vl(fonds: Fonds, points: list[tuple]) -> int:
    """Crée ou met à jour les VL (date, valeur) d'un fonds. Renvoie le nombre de points écrits."""
    objets = [ValeurLiquidative(fonds=fonds, date=d, valeur=float(v)) for d, v in points]
    with transaction.atomic():
        ValeurLiquidative.objects.bulk_create(objets, batch_size=2000, update_conflicts=True,
                                              unique_fields=["fonds", "date"], update_fields=["valeur"])
    return len(objets)


def enregistrer_actifs(fonds: Fonds, points: list[tuple]) -> int:
    objets = [ActifNet(fonds=fonds, date=d, montant=float(m)) for d, m in points]
    with transaction.atomic():
        ActifNet.objects.bulk_create(objets, batch_size=2000, update_conflicts=True,
                                     unique_fields=["fonds", "date"], update_fields=["montant"])
    return len(objets)


def remplacer_flux(fonds: Fonds, lignes: list[dict]) -> int:
    """Remplace les flux du fonds sur la période couverte par ``lignes`` (date, sens, type_client, montant)."""
    if not lignes:
        return 0
    dates = [l["date"] for l in lignes]
    with transaction.atomic():
        fonds.flux.filter(date__gte=min(dates), date__lte=max(dates)).delete()
        Flux.objects.bulk_create([Flux(fonds=fonds, **l) for l in lignes], batch_size=2000)
    return len(lignes)
