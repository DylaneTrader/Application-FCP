"""Figures Plotly, rendues côté navigateur par Plotly.js (voir static/fonds/app.js).

Les couleurs viennent de la SGO affichée ; fond transparent et couleur de texte héritée de la page, pour que
les graphiques suivent le thème clair ou sombre.
"""
from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go


def _rgba(hexa: str, alpha: float) -> str:
    h = hexa.lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"


def _figure(fig: go.Figure, hauteur: int = 380, **layout) -> dict:
    reglages = dict(height=hauteur, margin=dict(l=8, r=8, t=24, b=8), paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", separators=", ",
                    legend=dict(orientation="h", y=-0.12, x=0), font=dict(size=12))
    fig.update_layout(**{**reglages, **layout})
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(127,127,127,0.18)", zeroline=False)
    return json.loads(fig.to_json())


def courbe_vl(vl: pd.Series, couleurs, base100: bool = False) -> dict:
    y = vl / vl.iloc[0] * 100 if base100 else vl
    fig = go.Figure(go.Scatter(x=vl.index, y=y, mode="lines", name="Base 100" if base100 else "VL",
                               line=dict(color=couleurs.primaire, width=2), fill="tozeroy",
                               fillcolor=_rgba(couleurs.primaire, 0.07),
                               hovertemplate="%{y:,.2f}<extra></extra>"))
    lo, hi = float(y.min()), float(y.max())
    marge = (hi - lo) * 0.08 or hi * 0.01
    return _figure(fig, yaxis=dict(range=[lo - marge, hi + marge]), showlegend=False)


def courbe_drawdown(dd: pd.Series, couleurs) -> dict:
    fig = go.Figure(go.Scatter(x=dd.index, y=dd * 100, mode="lines", fill="tozeroy", name="Perte depuis le plus haut",
                               line=dict(color="#B3261E", width=1.5), fillcolor="rgba(179,38,30,0.12)",
                               hovertemplate="%{y:.2f} %<extra></extra>"))
    return _figure(fig, 240, yaxis=dict(ticksuffix=" %"), showlegend=False)


def barres_calendrier(lignes: list[dict], couleurs) -> dict:
    fig = go.Figure(go.Bar(
        x=[str(l["annee"]) + (" *" if l["partiel"] else "") for l in lignes], y=[l["rendement"] * 100 for l in lignes],
        marker_color=[couleurs.primaire if l["rendement"] >= 0 else "#B3261E" for l in lignes],
        text=[f"{l['rendement'] * 100:.2f} %".replace(".", ",") for l in lignes], textposition="outside",
        cliponaxis=False, hovertemplate="%{y:.2f} %<extra></extra>"))
    valeurs = [l["rendement"] * 100 for l in lignes] or [0]
    haut, bas = max(max(valeurs), 0), min(min(valeurs), 0)
    marge = (haut - bas) * 0.15 or 1
    return _figure(fig, 280, yaxis=dict(ticksuffix=" %", range=[bas - (marge if bas < 0 else 0), haut + marge]),
                   showlegend=False, hovermode="closest")


def eventail(tableau: pd.DataFrame, couleurs, objectif: float | None = None) -> dict:
    """Projection : bandes 5–95 % et 25–75 %, médiane, montant investi."""
    x = tableau["annee"]
    fig = go.Figure()
    for bas, haut, alpha, nom in (("q05", "q95", 0.12, "90 % des cas"), ("q25", "q75", 0.25, "50 % des cas")):
        fig.add_trace(go.Scatter(x=x, y=tableau[haut], mode="lines", line=dict(width=0), showlegend=False,
                                 hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=x, y=tableau[bas], mode="lines", line=dict(width=0), fill="tonexty",
                                 fillcolor=_rgba(couleurs.primaire, alpha), name=nom, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x, y=tableau["q50"], mode="lines", name="Scénario médian",
                             line=dict(color=couleurs.primaire, width=2.5), hovertemplate="%{y:,.0f}<extra>Médian</extra>"))
    fig.add_trace(go.Scatter(x=x, y=tableau["q05"], mode="lines", name="Scénario défavorable (5 %)",
                             line=dict(color=couleurs.secondaire, width=1, dash="dot"),
                             hovertemplate="%{y:,.0f}<extra>5 %</extra>"))
    fig.add_trace(go.Scatter(x=x, y=tableau["investi"], mode="lines", name="Montant investi",
                             line=dict(color="#7a7a7a", width=1.5, dash="dash"),
                             hovertemplate="%{y:,.0f}<extra>Investi</extra>"))
    if objectif:
        fig.add_hline(y=objectif, line=dict(color="#B07D10", dash="dot"), annotation_text="Objectif")
    return _figure(fig, 400, xaxis=dict(title="Années"))


def aires_simulation(tableau: pd.DataFrame, couleurs, reelle: pd.Series | None = None) -> dict:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tableau["annee"], y=tableau["investi"], mode="lines", stackgroup="v",
                             name="Montant investi", line=dict(color=couleurs.secondaire, width=0.5),
                             hovertemplate="%{y:,.0f}<extra>Investi</extra>"))
    fig.add_trace(go.Scatter(x=tableau["annee"], y=tableau["interets"].clip(lower=0), mode="lines", stackgroup="v",
                             name="Gains", line=dict(color=couleurs.primaire, width=0.5),
                             hovertemplate="%{y:,.0f}<extra>Gains</extra>"))
    if reelle is not None:
        fig.add_trace(go.Scatter(x=tableau["annee"], y=reelle, mode="lines", name="Valeur en pouvoir d'achat actuel",
                                 line=dict(color="#B07D10", width=2, dash="dot"),
                                 hovertemplate="%{y:,.0f}<extra>Réelle</extra>"))
    return _figure(fig, 360, xaxis=dict(title="Années"))


def courbe_retraits(tableau: pd.DataFrame, couleurs) -> dict:
    fig = go.Figure()
    for phase, couleur in (("Épargne", couleurs.primaire), ("Retraits", couleurs.secondaire)):
        t = tableau[tableau["phase"] == phase]
        fig.add_trace(go.Scatter(x=t["annee"], y=t["valeur"], mode="lines", name=phase, fill="tozeroy",
                                 line=dict(color=couleur, width=2), fillcolor=_rgba(couleur, 0.12),
                                 hovertemplate="%{y:,.0f}<extra></extra>"))
    return _figure(fig, 300, xaxis=dict(title="Années"))


def barres_flux(mensuel: pd.DataFrame, couleurs) -> dict:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=mensuel.index, y=mensuel.get("S", 0), name="Souscriptions", marker_color=couleurs.primaire,
                         hovertemplate="%{y:,.0f}<extra>Souscriptions</extra>"))
    fig.add_trace(go.Bar(x=mensuel.index, y=-mensuel.get("R", 0), name="Rachats", marker_color=couleurs.secondaire,
                         hovertemplate="%{y:,.0f}<extra>Rachats</extra>"))
    fig.add_trace(go.Scatter(x=mensuel.index, y=mensuel["net"], name="Collecte nette", mode="lines+markers",
                             line=dict(color="#B07D10", width=2), hovertemplate="%{y:,.0f}<extra>Net</extra>"))
    return _figure(fig, 360, barmode="relative")


def courbe_actifs(total: pd.Series, couleurs) -> dict:
    fig = go.Figure(go.Scatter(x=total.index, y=total, mode="lines", fill="tozeroy", name="Actifs nets",
                               line=dict(color=couleurs.primaire, width=2), fillcolor=_rgba(couleurs.primaire, 0.1),
                               hovertemplate="%{y:,.0f}<extra></extra>"))
    return _figure(fig, 320, showlegend=False)


def barres_repartition(parts: pd.Series, couleurs) -> dict:
    parts = parts.sort_values()
    fig = go.Figure(go.Bar(x=parts * 100, y=parts.index, orientation="h", marker_color=couleurs.primaire,
                           text=[f"{p * 100:.1f} %".replace(".", ",") for p in parts], textposition="outside",
                           hovertemplate="%{x:.1f} %<extra></extra>"))
    return _figure(fig, max(260, 26 * len(parts) + 60), xaxis=dict(ticksuffix=" %"), showlegend=False,
                   hovermode="closest")
