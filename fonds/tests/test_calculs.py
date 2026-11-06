"""Calculs purs : simulateur et analyse des VL."""
import math

import numpy as np
import pandas as pd
from django.test import SimpleTestCase

from fonds import analyse, simulation as S


class SimulateurTests(SimpleTestCase):
    def test_taux_effectif_annuel(self):
        self.assertAlmostEqual(S.valeur_finale(1000, 0, 0.06, 1), 1060, places=6)
        self.assertAlmostEqual(S.valeur_finale(1000, 0, 0.06, 10), 1000 * 1.06 ** 10, places=6)

    def test_versements_sans_rendement(self):
        self.assertAlmostEqual(S.valeur_finale(0, 100, 0, 2), 2400)

    def test_les_quatre_calculs_sont_coherents(self):
        cap, ver, taux, ans = 500_000, 25_000, 0.055, 12
        fv = S.valeur_finale(cap, ver, taux, ans)
        self.assertAlmostEqual(S.versement_necessaire(fv, cap, taux, ans), ver, places=4)
        self.assertAlmostEqual(S.capital_necessaire(fv, ver, taux, ans), cap, places=2)
        self.assertEqual(S.duree_necessaire(fv, cap, ver, taux), ans * 12)
        self.assertEqual(S.duree_necessaire(fv + 1, cap, ver, taux), ans * 12 + 1)

    def test_duree_taux_nul_ou_negatif_et_objectif_impossible(self):
        self.assertEqual(S.duree_necessaire(1200, 0, 100, 0), 12)
        self.assertIsNone(S.duree_necessaire(10_000_000, 1000, 0, -0.02))
        self.assertEqual(S.duree_necessaire(500, 1000, 0, 0.05), 0)

    def test_resoudre_et_echeancier(self):
        r = S.resoudre("versement", capital=0, taux=0.05, annees=10, objectif=10_000_000)
        self.assertAlmostEqual(r.valeur, 10_000_000, delta=1)
        self.assertEqual(len(r.tableau), 121)
        self.assertEqual(list(S.annuel(r.tableau)["mois"]), list(range(12, 121, 12)))
        with self.assertRaises(S.ErreurSimulation):
            S.resoudre("versement", taux=0.05, annees=10, objectif=0)
        with self.assertRaises(S.ErreurSimulation):
            S.resoudre("valeur_finale", capital=-1, taux=0.05, annees=10)

    def test_retrait_soutenable_epuise_le_capital(self):
        retrait = S.retrait_soutenable(1_000_000, 0.04, 10)
        t, constitue, epuise = S.retraits(1_000_000, 0, 0.04, 0, retrait, 10)
        self.assertAlmostEqual(t["valeur"].iloc[-1], 0, delta=1)
        t, _, epuise = S.retraits(1_000_000, 0, 0.04, 0, retrait * 1.2, 10)
        self.assertIsNotNone(epuise)
        self.assertLess(epuise, 120)

    def test_valeur_reelle(self):
        t = S.echeancier(1000, 0, 0.0, 12)
        self.assertAlmostEqual(S.valeur_reelle(t, 0.02).iloc[-1], 1000 / 1.02)


def vl_synthetique(taux=0.06, vol=0.0, annees=4, frequence="W-FRI", graine=0):
    dates = pd.date_range("2021-01-01", periods=int(annees * (52 if frequence.startswith("W") else 252)) + 1,
                          freq=frequence if frequence.startswith("W") else "B")
    ppa = 52 if frequence.startswith("W") else 252
    bruit = np.random.default_rng(graine).standard_normal(len(dates) - 1) * vol / np.sqrt(ppa)
    log = np.concatenate([[0], np.cumsum(np.log1p(taux) / ppa + bruit)])
    jours = (dates - dates[0]).days.to_numpy()
    if vol == 0:
        log = np.log1p(taux) * jours / 365.25
    return pd.Series(1000 * np.exp(log), index=dates)


class AnalyseTests(SimpleTestCase):
    def test_frequence_detectee(self):
        self.assertAlmostEqual(analyse.periodes_par_an(vl_synthetique()), 52, delta=1.5)
        self.assertAlmostEqual(analyse.periodes_par_an(vl_synthetique(frequence="B")), 261, delta=3)

    def test_performances_croissance_reguliere(self):
        vl = vl_synthetique(0.06, 0)
        perf = {p["periode"]: p for p in analyse.performances(vl)}
        self.assertAlmostEqual(perf["1 an"]["cumule"], 0.06, delta=0.002)
        self.assertAlmostEqual(perf["3 ans"]["annualise"], 0.06, delta=0.001)
        self.assertIsNone(perf["5 ans"]["cumule"])
        self.assertAlmostEqual(analyse.cagr(vl), 0.06, places=6)

    def test_calendrier_et_drawdown(self):
        vl = pd.Series([100, 110, 99, 121], index=pd.to_datetime(["2022-06-30", "2022-12-30", "2023-06-30", "2023-12-29"]))
        cal = analyse.calendrier(vl)
        self.assertAlmostEqual(cal[0]["rendement"], 0.10)
        self.assertTrue(cal[0]["partiel"])
        self.assertAlmostEqual(cal[1]["rendement"], 0.10)
        self.assertAlmostEqual(analyse.drawdowns(vl).min(), -0.10)

    def test_rendement_attendu_retrouve_le_taux(self):
        e = analyse.rendement_attendu(vl_synthetique(0.06, 0))
        self.assertAlmostEqual(e["taux_median"], 0.06, delta=0.001)
        self.assertLess(e["sigma"], 1e-6)
        e = analyse.rendement_attendu(vl_synthetique(0.08, 0.15, annees=10))
        self.assertGreater(e["taux_moyen"], e["taux_median"])
        self.assertAlmostEqual(e["sigma"], 0.15, delta=0.02)
        self.assertIsNotNone(e["glissant"])
        self.assertIsNone(analyse.rendement_attendu(vl_synthetique(annees=0.2)))

    def test_projection(self):
        p = analyse.projection(math.log(1.06), 0.10, 5, 1_000_000, 10_000, objectif=1_500_000)
        t = p["tableau"]
        self.assertEqual(len(t), 61)
        self.assertTrue((t["q05"] <= t["q25"]).all() and (t["q25"] <= t["q50"]).all() and (t["q50"] <= t["q95"]).all())
        self.assertAlmostEqual(p["investi"], 1_600_000)
        self.assertTrue(0 < p["probabilite_perte"] < 0.5)
        sans_risque = analyse.projection(math.log(1.06), 0.0, 5, 1_000_000)
        self.assertAlmostEqual(sans_risque["finales"]["q50"], 1_000_000 * 1.06 ** 5, delta=1)
        self.assertEqual(sans_risque["probabilite_perte"], 0)
