"""Nombres à la française : espace fine insécable pour les milliers, virgule décimale."""
import math

from django import template

register = template.Library()
ESPACE = " "


def _vide(x) -> bool:
    return x is None or (isinstance(x, float) and not math.isfinite(x))


@register.filter
def nombre(x, decimales=0):
    if _vide(x):
        return "n.d."
    texte = f"{float(x):,.{int(decimales)}f}"
    return texte.replace(",", ESPACE).replace(".", ",")


@register.filter
def montant(x, devise="FCFA"):
    return "n.d." if _vide(x) else f"{nombre(x)} {devise}"


@register.filter
def pct(x, decimales=2):
    return "n.d." if _vide(x) else f"{nombre(float(x) * 100, decimales)} %"


@register.filter
def pct_signe(x, decimales=2):
    if _vide(x):
        return "n.d."
    return ("+" if x > 0 else "") + pct(x, decimales)


@register.filter
def get_item(dictionnaire, cle):
    return dictionnaire.get(cle) if isinstance(dictionnaire, dict) else None


@register.filter
def signe(x):
    """Classe CSS selon le signe."""
    if _vide(x):
        return ""
    return "hausse" if x > 0 else "baisse" if x < 0 else ""
