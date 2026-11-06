"""Import, API et pages, sur une base de test."""
import tempfile
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from fonds.importation import importer_classeur, normaliser
from fonds.models import SGO, Flux, Fonds, ValeurLiquidative
from fonds.tests.test_calculs import vl_synthetique


def classeur(chemin: Path):
    vl = vl_synthetique(0.06, 0.03, annees=3)
    with pd.ExcelWriter(chemin) as x:
        pd.DataFrame({"Date": vl.index.strftime("%d/%m/%Y"), "FCP Alpha": vl.values,
                      "FCP Beta-Monétaire": vl.values * 1.5}).to_excel(x, sheet_name="Valeurs Liquidatives", index=False)
        pd.DataFrame({"Date": vl.index[::4], "FCP ALPHA": 1e9, "FCP Beta Monetaire": 5e8}).to_excel(
            x, sheet_name="Actifs Nets", index=False)
        pd.DataFrame({"Date": vl.index[:6], "Type de clients": ["Particuliers", "Institutionnels"] * 3,
                      "Opérations": ["Souscriptions", "Rachats"] * 3, "FCP": "FCP Alpha",
                      "Montant": [100, 40, 200, 10, 50, 5]}).to_excel(x, sheet_name="Souscriptions Rachats", index=False)


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sgo = SGO.objects.create(nom="SGO Test", couleur_primaire="#123456")
        cls.autre = SGO.objects.create(nom="Autre SGO")
        with tempfile.TemporaryDirectory() as d:
            classeur(Path(d) / "c.xlsx")
            cls.rapport = importer_classeur(Path(d) / "c.xlsx", cls.sgo)
        cls.alpha = Fonds.objects.get(sgo=cls.sgo, nom="FCP Alpha")
        cls.membre = User.objects.create_user("membre", password="x-test-123")
        cls.sgo.membres.add(cls.membre)
        cls.etranger = User.objects.create_user("etranger", password="x-test-123")


class ImportTests(Base):
    def test_noms_rapproches_et_categorie(self):
        self.assertEqual(normaliser("FCP Beta-Monétaire"), normaliser("FCP BETA MONETAIRE"))
        self.assertEqual(sorted(self.rapport.fonds_crees), ["FCP Alpha", "FCP Beta-Monétaire"])
        self.assertEqual(Fonds.objects.get(nom="FCP Beta-Monétaire").categorie, "monetaire")
        self.assertEqual(self.alpha.actifs_nets.count(), self.alpha.vls.count() // 4 + 1)
        self.assertEqual(self.alpha.flux.filter(sens="R").count(), 3)

    def test_reimport_idempotent(self):
        avant = (ValeurLiquidative.objects.count(), Flux.objects.count())
        with tempfile.TemporaryDirectory() as d:
            classeur(Path(d) / "c.xlsx")
            r = importer_classeur(Path(d) / "c.xlsx", self.sgo)
        self.assertEqual(r.fonds_crees, [])
        self.assertEqual((ValeurLiquidative.objects.count(), Flux.objects.count()), avant)

    def test_alias(self):
        self.alpha.alias = "ALPHA FUND"
        self.alpha.save()
        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame({"Date": ["03/01/2025"], "Alpha Fund": [999.0]}).to_csv(Path(d) / "v.csv", index=False)
            r = importer_classeur(Path(d) / "v.csv", self.sgo)
        self.assertEqual(r.fonds_crees, [])
        self.assertTrue(self.alpha.vls.filter(valeur=999.0).exists())


class APITests(Base):
    def setUp(self):
        self.client = APIClient()

    def test_lecture_publique(self):
        r = self.client.get("/api/fonds/", {"sgo": self.sgo.slug})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 2)
        self.assertIsNotNone(r.json()["results"][0]["derniere_vl"])
        r = self.client.get(f"/api/fonds/{self.alpha.pk}/vl/", {"debut": "2023-01-01"})
        self.assertTrue(all(p["date"] >= "2023-01-01" for p in r.json()))
        r = self.client.get(f"/api/fonds/{self.alpha.pk}/rendement-attendu/", {"annees": 3, "horizon": 4})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["trajectoire_annuelle"]), 5)
        self.assertEqual(self.client.get(f"/api/fonds/{self.alpha.pk}/performances/").status_code, 200)
        self.assertEqual(self.client.get("/api/sgo/sgo-test/").json()["couleur_primaire"], "#123456")

    def test_donnees_privees(self):
        self.assertIn(self.client.get(f"/api/fonds/{self.alpha.pk}/flux/").status_code, (401, 403))
        self.client.force_authenticate(self.etranger)
        self.assertEqual(self.client.get(f"/api/fonds/{self.alpha.pk}/actifs-nets/").status_code, 403)
        self.client.force_authenticate(self.membre)
        self.assertEqual(len(self.client.get(f"/api/fonds/{self.alpha.pk}/flux/").json()), 6)

    def test_ecriture_vl_par_jeton(self):
        donnees = [{"date": "2030-01-04", "valeur": 2000.5}]
        self.assertIn(self.client.post(f"/api/fonds/{self.alpha.pk}/vl/", donnees, format="json").status_code,
                      (401, 403))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.etranger).key}")
        self.assertEqual(self.client.post(f"/api/fonds/{self.alpha.pk}/vl/", donnees, format="json").status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.membre).key}")
        r = self.client.post(f"/api/fonds/{self.alpha.pk}/vl/", donnees, format="json")
        self.assertEqual(r.status_code, 201)
        r = self.client.post(f"/api/fonds/{self.alpha.pk}/vl/", [{"date": "2030-01-04", "valeur": 2001}], format="json")
        self.assertEqual(self.alpha.vls.get(date="2030-01-04").valeur, 2001)
        self.assertEqual(self.client.post(f"/api/fonds/{self.alpha.pk}/vl/", [{"date": "x", "valeur": -1}],
                                          format="json").status_code, 400)

    def test_simulation(self):
        r = self.client.post("/api/simulation/", {"calcul": "duree", "capital_initial": 0, "versement_mensuel": 100,
                                                  "taux_annuel": 0, "objectif": 1200}, format="json")
        self.assertEqual(r.json()["duree_mois"], 12)
        r = self.client.post("/api/simulation/", {"calcul": "versement", "taux_annuel": 0.05, "objectif": 0},
                             format="json")
        self.assertEqual(r.status_code, 400)


class PagesTests(Base):
    def test_pages_publiques(self):
        s, f = self.sgo.slug, self.alpha.slug
        for url in ["/", "/a-propos/", f"/sgo/{s}/", f"/sgo/{s}/fonds/{f}/", f"/sgo/{s}/fonds/{f}/?periode=ytd&base100=1",
                    f"/sgo/{s}/fonds/{f}/rendement-attendu/?annees=&horizon=10&objectif=2000000",
                    f"/sgo/{s}/simulateur/", f"/sgo/{s}/simulateur/?calcul=duree&objectif=1&capital=0&versement=0",
                    f"/sgo/{s}/simulateur/?fonds={f}&calcul=versement&retrait=50000&inflation=3",
                    "/comptes/login/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_couleurs_de_la_sgo(self):
        self.assertContains(self.client.get(f"/sgo/{self.sgo.slug}/"), "--primaire: #123456")

    def test_csv_et_htmx(self):
        r = self.client.get(f"/sgo/{self.sgo.slug}/fonds/{self.alpha.slug}/?periode=1a&format=csv")
        self.assertEqual(r["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Date;Valeur liquidative", r.content.decode("utf-8-sig"))
        r = self.client.get(f"/sgo/{self.sgo.slug}/simulateur/", HTTP_HX_REQUEST="true")
        self.assertNotContains(r, "<html")
        self.assertContains(r, "Valeur finale")

    def test_pages_membres(self):
        for nom in ("souscriptions-rachats", "actifs-nets"):
            url = f"/sgo/{self.sgo.slug}/{nom}/"
            self.assertEqual(self.client.get(url).status_code, 302)
            self.client.force_login(self.etranger)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.client.force_login(self.membre)
            self.assertEqual(self.client.get(url).status_code, 200)
            self.client.logout()
        self.client.force_login(self.membre)
        self.assertContains(self.client.get(f"/sgo/{self.sgo.slug}/"), "Actifs nets gérés")

    def test_introuvable(self):
        self.assertEqual(self.client.get("/sgo/inconnue/").status_code, 404)
        self.assertEqual(self.client.get(f"/sgo/{self.autre.slug}/fonds/{self.alpha.slug}/").status_code, 404)
