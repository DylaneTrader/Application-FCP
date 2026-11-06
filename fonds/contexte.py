"""Couleurs et logo de la SGO affichée, disponibles dans tous les gabarits."""
from dataclasses import dataclass

from django.templatetags.static import static

from .models import SGO

DEFAUT = SGO._meta.get_field


@dataclass(frozen=True)
class Couleurs:
    primaire: str
    secondaire: str
    accent: str


COULEURS_DEFAUT = Couleurs(DEFAUT("couleur_primaire").default, DEFAUT("couleur_secondaire").default,
                           DEFAUT("couleur_accent").default)


def couleurs(sgo: SGO | None) -> Couleurs:
    if sgo is None:
        return COULEURS_DEFAUT
    return Couleurs(sgo.couleur_primaire, sgo.couleur_secondaire, sgo.couleur_accent)


def logo(sgo: SGO | None) -> str | None:
    if sgo is None:
        return None
    if sgo.logo:
        return sgo.logo.url
    return static(sgo.logo_statique) if sgo.logo_statique else None


def theme(request):
    sgo = getattr(request, "sgo", None)
    return {"sgo_courante": sgo, "couleurs": couleurs(sgo), "logo_sgo": logo(sgo),
            "membre_sgo": bool(sgo and sgo.est_membre(request.user))}
