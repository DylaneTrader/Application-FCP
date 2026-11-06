"""API REST ouverte à toute SGO.

Lecture publique : SGO, fonds, VL, performances, rendement attendu, simulateur.
Écriture des VL, et lecture comme écriture des actifs nets et des flux : membres de la SGO du fonds,
authentifiés par jeton (en-tête ``Authorization: Token <jeton>``) ou par session.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import analyse, donnees, simulation
from .models import SGO, Flux, Fonds


def _propre(x):
    """Nombres JSON valides : NaN et infinis deviennent null, dates en ISO."""
    if isinstance(x, dict):
        return {k: _propre(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_propre(v) for v in x]
    if isinstance(x, pd.Timestamp):
        return x.date().isoformat()
    if isinstance(x, (np.floating, float)):
        return None if not math.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    return x


# ---------- Sérialiseurs ----------

class SGOSerializer(serializers.ModelSerializer):
    nombre_fonds = serializers.IntegerField(source="fonds.count", read_only=True)

    class Meta:
        model = SGO
        fields = ["nom", "slug", "pays", "site_web", "couleur_primaire", "couleur_secondaire", "couleur_accent",
                  "taux_sans_risque", "nombre_fonds"]


class FondsSerializer(serializers.ModelSerializer):
    sgo = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    derniere_vl = serializers.SerializerMethodField()

    class Meta:
        model = Fonds
        fields = ["id", "sgo", "nom", "slug", "categorie", "devise", "actif", "description", "derniere_vl"]

    def get_derniere_vl(self, fonds):
        vl = fonds.vls.order_by("-date").first()
        return {"date": vl.date, "valeur": vl.valeur} if vl else None


class PointVL(serializers.Serializer):
    date = serializers.DateField()
    valeur = serializers.FloatField(min_value=1e-9)


class PointActif(serializers.Serializer):
    date = serializers.DateField()
    montant = serializers.FloatField(min_value=0)


class PointFlux(serializers.Serializer):
    date = serializers.DateField()
    sens = serializers.ChoiceField(choices=Flux.Sens.choices)
    type_client = serializers.CharField(max_length=80, allow_blank=True, default="")
    montant = serializers.FloatField(min_value=0)


class DemandeSimulation(serializers.Serializer):
    calcul = serializers.ChoiceField(choices=list(simulation.CALCULS), default="valeur_finale")
    capital_initial = serializers.FloatField(min_value=0, default=0)
    versement_mensuel = serializers.FloatField(min_value=0, default=0)
    taux_annuel = serializers.FloatField(min_value=-0.99, max_value=1, help_text="Décimal : 0,05 = 5 %.")
    duree_annees = serializers.FloatField(min_value=0, max_value=100, default=10)
    objectif = serializers.FloatField(min_value=0, default=0)


# ---------- Vues ----------

class SGOViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SGO.objects.prefetch_related("fonds")
    serializer_class = SGOSerializer
    lookup_field = "slug"


class FondsViewSet(viewsets.ReadOnlyModelViewSet):
    """Fonds ; filtres ``?sgo=<slug>`` et ``?categorie=<code>``."""
    serializer_class = FondsSerializer

    def get_queryset(self):
        qs = Fonds.objects.select_related("sgo")
        if sgo := self.request.query_params.get("sgo"):
            qs = qs.filter(sgo__slug=sgo)
        if categorie := self.request.query_params.get("categorie"):
            qs = qs.filter(categorie=categorie)
        return qs

    def _membre(self, fonds):
        if not fonds.sgo.est_membre(self.request.user):
            raise PermissionDenied("Réservé aux membres de la SGO du fonds.")

    def _ecrire(self, request, fonds, point, ecrire):
        self._membre(fonds)
        s = point(data=request.data, many=True)
        s.is_valid(raise_exception=True)
        n = ecrire(fonds, s.validated_data)
        return Response({"enregistres": n}, status=status.HTTP_201_CREATED)

    def _periode(self, qs):
        p = self.request.query_params
        try:
            if p.get("debut"):
                qs = qs.filter(date__gte=pd.Timestamp(p["debut"]).date())
            if p.get("fin"):
                qs = qs.filter(date__lte=pd.Timestamp(p["fin"]).date())
        except ValueError:
            raise ValidationError("Dates au format AAAA-MM-JJ.") from None
        return qs

    @action(detail=True, methods=["get", "post"])
    def vl(self, request, pk=None):
        """GET : VL du fonds (``?debut=&fin=``). POST : liste de ``{date, valeur}``, créées ou mises à jour."""
        fonds = self.get_object()
        if request.method == "POST":
            return self._ecrire(request, fonds, PointVL,
                                lambda f, d: donnees.enregistrer_vl(f, [(p["date"], p["valeur"]) for p in d]))
        qs = self._periode(fonds.vls.order_by("date")).values("date", "valeur")
        return Response(list(qs))

    @action(detail=True, methods=["get", "post"], url_path="actifs-nets")
    def actifs_nets(self, request, pk=None):
        fonds = self.get_object()
        if request.method == "POST":
            return self._ecrire(request, fonds, PointActif,
                                lambda f, d: donnees.enregistrer_actifs(f, [(p["date"], p["montant"]) for p in d]))
        self._membre(fonds)
        return Response(list(self._periode(fonds.actifs_nets.order_by("date")).values("date", "montant")))

    @action(detail=True, methods=["get", "post"])
    def flux(self, request, pk=None):
        """POST : remplace les flux du fonds sur la période couverte par la liste envoyée."""
        fonds = self.get_object()
        if request.method == "POST":
            return self._ecrire(request, fonds, PointFlux, lambda f, d: donnees.remplacer_flux(f, list(d)))
        self._membre(fonds)
        return Response(list(self._periode(fonds.flux.order_by("date"))
                             .values("date", "sens", "type_client", "montant")))

    @action(detail=True, methods=["get"])
    def performances(self, request, pk=None):
        fonds = self.get_object()
        vl = donnees.serie_vl(fonds)
        return Response(_propre({"performances": analyse.performances(vl), "calendrier": analyse.calendrier(vl),
                                 "risque": analyse.indicateurs_risque(vl, fonds.sgo.taux_sans_risque)}))

    @action(detail=True, methods=["get"], url_path="rendement-attendu")
    def rendement_attendu(self, request, pk=None):
        """``?annees=3`` (historique retenu, vide = tout), ``&horizon=5&capital=1000000&versement=0``."""
        fonds = self.get_object()
        p = request.query_params
        try:
            annees = int(p["annees"]) if p.get("annees") else None
            horizon = min(max(int(p.get("horizon", 5)), 1), 40)
            capital, versement = float(p.get("capital", 1_000_000)), float(p.get("versement", 0))
        except ValueError:
            raise ValidationError("Paramètres numériques invalides.") from None
        estimation = analyse.rendement_attendu(donnees.serie_vl(fonds), annees)
        if estimation is None:
            return Response({"detail": "Historique insuffisant (au moins six mois de VL)."}, status=422)
        proj = analyse.projection(estimation["mu"], estimation["sigma"], horizon, capital, versement)
        annuel = proj["tableau"][proj["tableau"]["annee"] % 1 == 0]
        return Response(_propre({"estimation": estimation, "horizon": horizon, "investi": proj["investi"],
                                 "probabilite_perte": proj["probabilite_perte"], "valeurs_finales": proj["finales"],
                                 "trajectoire_annuelle": annuel.to_dict("records")}))


class SimulationView(APIView):
    """Simulateur de placement : calcule la grandeur ``calcul`` à partir des trois autres."""
    permission_classes = [AllowAny]

    def post(self, request):
        s = DemandeSimulation(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        try:
            r = simulation.resoudre(d["calcul"], capital=d["capital_initial"], versement=d["versement_mensuel"],
                                    taux=d["taux_annuel"], annees=d["duree_annees"], objectif=d["objectif"])
        except simulation.ErreurSimulation as erreur:
            raise ValidationError(str(erreur)) from None
        reponse = {"calcul": r.calcul, "capital_initial": r.capital, "versement_mensuel": r.versement,
                   "taux_annuel": r.taux, "duree_mois": r.mois, "objectif": r.objectif, "valeur_finale": r.valeur,
                   "atteignable": r.mois is not None}
        if r.tableau is not None:
            reponse["echeancier_annuel"] = simulation.annuel(r.tableau).to_dict("records")
        return Response(_propre(reponse))
