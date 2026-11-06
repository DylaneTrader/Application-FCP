"""Pages HTML : tableau des fonds, historique des VL, rendement attendu, simulateur, flux et actifs nets."""
from __future__ import annotations

import csv
import math
from functools import wraps

import pandas as pd
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from . import analyse, donnees, graphiques, simulation
from .contexte import couleurs
from .models import SGO, Fonds

PERIODES = {"1m": ("1 mois", pd.DateOffset(months=1)), "6m": ("6 mois", pd.DateOffset(months=6)),
            "ytd": ("Depuis le 1er janvier", None), "1a": ("1 an", pd.DateOffset(years=1)),
            "3a": ("3 ans", pd.DateOffset(years=3)), "5a": ("5 ans", pd.DateOffset(years=5)),
            "max": ("Tout l'historique", None)}
FENETRES = {"1": "1 an", "3": "3 ans", "5": "5 ans", "": "Tout l'historique"}


def _nombre(valeur, defaut: float, mini: float | None = None, maxi: float | None = None) -> float:
    try:
        x = float(str(valeur).replace(" ", "").replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return defaut
    if mini is not None:
        x = max(x, mini)
    if maxi is not None:
        x = min(x, maxi)
    return x


def avec_sgo(membres: bool = False):
    """Charge la SGO de l'URL dans ``request.sgo`` ; ``membres`` : page réservée à ses membres."""
    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, sgo, *args, **kwargs):
            request.sgo = get_object_or_404(SGO, slug=sgo)
            if membres and not request.sgo.est_membre(request.user):
                if not request.user.is_authenticated:
                    return redirect_to_login(request.get_full_path())
                raise PermissionDenied("Page réservée aux membres de la SGO.")
            return vue(request, request.sgo, *args, **kwargs)
        return enveloppe
    return decorateur


def _fonds(sgo: SGO, slug: str) -> Fonds:
    return get_object_or_404(Fonds, sgo=sgo, slug=slug)


def accueil(request):
    sgos = SGO.objects.annotate(nombre_fonds=Count("fonds", distinct=True), derniere_vl=Max("fonds__vls__date"))
    return render(request, "fonds/accueil.html", {"sgos": sgos})


def a_propos(request):
    return render(request, "fonds/a_propos.html")


@avec_sgo()
def tableau_sgo(request, sgo):
    categorie = request.GET.get("categorie", "")
    lignes, sans_vl = [], 0
    for f in sgo.fonds.filter(actif=True):
        vl = donnees.serie_vl(f)
        if vl.empty:
            sans_vl += 1
            continue
        if categorie and f.categorie != categorie:
            continue
        perf = {p["periode"]: p for p in analyse.performances(vl)}
        risque = analyse.indicateurs_risque(vl, sgo.taux_sans_risque)
        lignes.append({"fonds": f, "date": vl.index[-1], "vl": vl.iloc[-1],
                       "ytd": perf.get("Depuis le 1er janvier", {}).get("cumule"),
                       "un_an": perf.get("1 an", {}).get("cumule"),
                       "trois_ans": perf.get("3 ans", {}).get("annualise"),
                       "volatilite": risque.get("Volatilité annualisée")})
    contexte = {"sgo": sgo, "lignes": lignes, "sans_vl": sans_vl, "categorie": categorie,
                "categories": [(c, n) for c, n in Fonds.Categorie.choices
                               if sgo.fonds.filter(categorie=c, vls__isnull=False).exists()],
                "derniere_date": max((l["date"] for l in lignes), default=None)}
    if sgo.est_membre(request.user):
        actifs = donnees.actifs_sgo(sgo)
        if not actifs.empty:
            contexte["encours"] = float(actifs.ffill().iloc[-1].sum())
            contexte["date_encours"] = actifs.index[-1]
    return render(request, "fonds/sgo.html", contexte)


def _periode(vl: pd.Series, code: str) -> pd.Series:
    fin = vl.index[-1]
    if code == "ytd":
        debut = pd.Timestamp(fin.year - 1, 12, 31)
    elif code in PERIODES and PERIODES[code][1] is not None:
        debut = fin - PERIODES[code][1]
    else:
        return vl
    avant = vl.loc[:debut]
    depart = avant.index[-1] if len(avant) else vl.index[0]   # inclut la dernière VL connue au début
    return vl.loc[depart:]


@avec_sgo()
def fiche_fonds(request, sgo, fonds):
    f = _fonds(sgo, fonds)
    vl = donnees.serie_vl(f)
    if vl.empty:
        return render(request, "fonds/fiche.html", {"sgo": sgo, "fonds": f, "vide": True})
    code = request.GET.get("periode", "1a" if (vl.index[-1] - vl.index[0]).days > 400 else "max")
    code = code if code in PERIODES else "max"
    base100 = request.GET.get("base100") == "1"
    partie = _periode(vl, code)
    if request.GET.get("format") == "csv":
        reponse = HttpResponse(content_type="text/csv; charset=utf-8")
        reponse["Content-Disposition"] = f'attachment; filename="vl_{f.slug}_{code}.csv"'
        reponse.write("﻿")
        ecrivain = csv.writer(reponse, delimiter=";")
        ecrivain.writerow(["Date", "Valeur liquidative"])
        for d, v in partie.items():
            ecrivain.writerow([d.strftime("%d/%m/%Y"), f"{v:.4f}".replace(".", ",")])
        return reponse
    c = couleurs(sgo)
    dernieres = pd.DataFrame({"vl": vl, "variation": vl.pct_change()}).tail(12).iloc[::-1]
    contexte = {
        "sgo": sgo, "fonds": f, "periodes": {k: v[0] for k, v in PERIODES.items()}, "periode": code,
        "base100": base100, "derniere": vl.iloc[-1], "date": vl.index[-1], "debut": vl.index[0],
        "variation": partie.iloc[-1] / partie.iloc[0] - 1 if len(partie) > 1 else None,
        "performances": analyse.performances(vl), "calendrier": analyse.calendrier(vl),
        "risque": analyse.indicateurs_risque(partie, sgo.taux_sans_risque),
        "dernieres": dernieres.itertuples(), "nombre": len(vl),
        "fig_vl": graphiques.courbe_vl(partie, c, base100),
        "fig_dd": graphiques.courbe_drawdown(analyse.drawdowns(partie), c),
        "fig_cal": graphiques.barres_calendrier(analyse.calendrier(vl), c),
    }
    return render(request, "fonds/fiche.html", contexte)


@avec_sgo()
def rendement_attendu(request, sgo, fonds):
    f = _fonds(sgo, fonds)
    vl = donnees.serie_vl(f)
    fenetre = request.GET.get("annees", "3")
    fenetre = fenetre if fenetre in FENETRES else "3"
    horizon = int(_nombre(request.GET.get("horizon"), 5, 1, 40))
    capital = _nombre(request.GET.get("capital"), 1_000_000, 0)
    versement = _nombre(request.GET.get("versement"), 0, 0)
    objectif = _nombre(request.GET.get("objectif"), 0, 0) or None
    comparaison = []
    for code, nom in FENETRES.items():
        e = analyse.rendement_attendu(vl, int(code) if code else None) if len(vl) else None
        comparaison.append({"code": code, "nom": nom, "estimation": e})
    estimation = next(l["estimation"] for l in comparaison if l["code"] == fenetre)
    contexte = {"sgo": sgo, "fonds": f, "fenetres": FENETRES, "fenetre": fenetre, "horizon": horizon,
                "capital": capital, "versement": versement, "objectif": objectif, "comparaison": comparaison,
                "estimation": estimation}
    if estimation:
        proj = analyse.projection(estimation["mu"], estimation["sigma"], horizon, capital, versement, objectif)
        contexte.update(projection=proj, fig=graphiques.eventail(proj["tableau"], couleurs(sgo), objectif),
                        annuel=proj["tableau"][proj["tableau"]["annee"] % 1 == 0].iloc[1:].itertuples())
    return render(request, "fonds/rendement.html", contexte)


def _taux_des_fonds(sgo: SGO) -> list[dict]:
    """Rendement attendu médian (3 ans, sinon tout l'historique) de chaque fonds, pour le simulateur."""
    sortie = []
    for f in sgo.fonds.filter(actif=True):
        vl = donnees.serie_vl(f)
        if vl.empty:
            continue
        e = analyse.rendement_attendu(vl, 3) or analyse.rendement_attendu(vl)
        if e:
            sortie.append({"fonds": f, "taux": e["taux_median"], "sigma": e["sigma"]})
    return sortie


@avec_sgo()
def simulateur(request, sgo):
    g = request.GET
    taux_fonds = _taux_des_fonds(sgo)
    choix_fonds = g.get("fonds", "")
    fonds_choisi = next((t for t in taux_fonds if t["fonds"].slug == choix_fonds), None)
    p = {
        "calcul": g.get("calcul") if g.get("calcul") in simulation.CALCULS else "valeur_finale",
        "capital": _nombre(g.get("capital"), 1_000_000, 0),
        "versement": _nombre(g.get("versement"), 50_000, 0),
        "objectif": _nombre(g.get("objectif"), 10_000_000, 0),
        "annees": _nombre(g.get("annees"), 10, 0.0833, 100),
        "taux": _nombre(g.get("taux"), round(fonds_choisi["taux"] * 100, 2) if fonds_choisi else 5.0, -99, 100),
        "inflation": _nombre(g.get("inflation"), 2.0, 0, 50),
        "retrait": _nombre(g.get("retrait"), 0, 0),
        "annees_retrait": _nombre(g.get("annees_retrait"), 15, 1, 60),
        "fonds": choix_fonds,
    }
    contexte = {"sgo": sgo, "p": p, "calculs": simulation.CALCULS, "taux_fonds": taux_fonds,
                "fonds_choisi": fonds_choisi}
    try:
        r = simulation.resoudre(p["calcul"], capital=p["capital"], versement=p["versement"], taux=p["taux"] / 100,
                                annees=p["annees"], objectif=p["objectif"])
    except simulation.ErreurSimulation as erreur:
        contexte["erreur"] = str(erreur)
        r = None
    if r is not None:
        contexte["r"] = r
        if r.tableau is not None:
            c = couleurs(sgo)
            reelle = simulation.valeur_reelle(r.tableau, p["inflation"] / 100) if p["inflation"] else None
            investi = float(r.tableau["investi"].iloc[-1])
            contexte.update(
                investi=investi, gains=r.valeur - investi, annees_resultat=r.mois / 12,
                part_gains=(r.valeur - investi) / investi if investi else None,
                valeur_reelle=float(reelle.iloc[-1]) if reelle is not None else None,
                annuel=simulation.annuel(r.tableau).itertuples(),
                fig=graphiques.aires_simulation(r.tableau, c, reelle),
                equivalents={"Par mois": r.versement, "Par trimestre": r.versement * 3, "Par an": r.versement * 12})
            contexte["retrait_soutenable"] = simulation.retrait_soutenable(r.valeur, p["taux"] / 100,
                                                                           p["annees_retrait"])
            if p["retrait"] > 0:
                t, constitue, epuise = simulation.retraits(r.capital, r.versement, p["taux"] / 100, r.mois / 12,
                                                           p["retrait"], p["annees_retrait"])
                contexte.update(fig_retraits=graphiques.courbe_retraits(t, c), epuise=epuise,
                                epuise_apres=(epuise - r.mois) / 12 if epuise else None,
                                capital_restant=float(t["valeur"].iloc[-1]))
        if fonds_choisi and r.tableau is not None and r.mois:
            # Même placement, mais avec la volatilité historique du fonds : fourchette de résultats possibles.
            contexte["proj"] = analyse.projection(math.log1p(p["taux"] / 100), fonds_choisi["sigma"], r.mois / 12,
                                                  r.capital, r.versement, r.objectif)
    gabarit = "fonds/_simulation.html" if request.headers.get("HX-Request") else "fonds/simulateur.html"
    return render(request, gabarit, contexte)


@avec_sgo(membres=True)
def flux(request, sgo):
    df = donnees.flux_sgo(sgo)
    contexte = {"sgo": sgo, "vide": df.empty}
    if df.empty:
        return render(request, "fonds/flux.html", contexte)
    fin_max, debut_min = df["date"].max(), df["date"].min()
    debut = pd.Timestamp(request.GET.get("debut") or max(debut_min, fin_max - pd.DateOffset(years=1)))
    fin = pd.Timestamp(request.GET.get("fin") or fin_max)
    choix = request.GET.get("fonds", "")
    d = df[(df["date"] >= debut) & (df["date"] <= fin)]
    if choix:
        d = d[d["fonds"] == choix]
    souscriptions, rachats = d.loc[d["sens"] == "S", "montant"].sum(), d.loc[d["sens"] == "R", "montant"].sum()
    mensuel = d.pivot_table(index=d["date"].dt.to_period("M").dt.to_timestamp(), columns="sens", values="montant",
                            aggfunc="sum").fillna(0)
    for s in ("S", "R"):
        if s not in mensuel:
            mensuel[s] = 0.0
    mensuel["net"] = mensuel["S"] - mensuel["R"]

    def tableau(cle):
        t = d.pivot_table(index=cle, columns="sens", values="montant", aggfunc="sum").fillna(0)
        for s in ("S", "R"):
            if s not in t:
                t[s] = 0.0
        t["net"] = t["S"] - t["R"]
        t["part"] = t["S"] / souscriptions if souscriptions else 0
        return t.sort_values("net", ascending=False).itertuples()

    contexte.update(debut=debut, fin=fin, debut_min=debut_min, fin_max=fin_max, choix=choix,
                    noms_fonds=sorted(df["fonds"].unique()), souscriptions=souscriptions, rachats=rachats,
                    net=souscriptions - rachats, operations=len(d),
                    taux_rachat=rachats / souscriptions if souscriptions else None,
                    fig=graphiques.barres_flux(mensuel, couleurs(sgo)),
                    par_type=tableau("type_client"), par_fonds=None if choix else tableau("fonds"))
    return render(request, "fonds/flux.html", contexte)


@avec_sgo(membres=True)
def actifs_nets(request, sgo):
    actifs = donnees.actifs_sgo(sgo)
    contexte = {"sgo": sgo, "vide": actifs.empty}
    if actifs.empty:
        return render(request, "fonds/actifs.html", contexte)
    rempli = actifs.ffill()
    total = rempli.sum(axis=1)
    dernier = rempli.iloc[-1].dropna()
    dernier = dernier[dernier > 0]
    il_y_a_un_an = rempli.loc[:actifs.index[-1] - pd.DateOffset(years=1)]
    precedent = il_y_a_un_an.iloc[-1] if len(il_y_a_un_an) else None
    lignes = [{"nom": nom, "montant": m, "part": m / dernier.sum(),
               "evolution": (m / precedent[nom] - 1) if precedent is not None and precedent.get(nom, 0) > 0 else None,
               "fonds": sgo.fonds.filter(nom=nom).first()}
              for nom, m in dernier.sort_values(ascending=False).items()]
    c = couleurs(sgo)
    contexte.update(date=actifs.index[-1], total=total.iloc[-1], lignes=lignes,
                    evolution=total.iloc[-1] / float(il_y_a_un_an.sum(axis=1).iloc[-1]) - 1
                    if len(il_y_a_un_an) and il_y_a_un_an.sum(axis=1).iloc[-1] > 0 else None,
                    fig_total=graphiques.courbe_actifs(total, c),
                    fig_parts=graphiques.barres_repartition(dernier / dernier.sum(), c))
    return render(request, "fonds/actifs.html", contexte)
