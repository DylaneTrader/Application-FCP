# Plateforme FCP

Application Django ouverte à toute société de gestion d'OPCVM (SGO) : valeurs liquidatives de ses FCP,
rendement attendu, simulateur de placement, souscriptions et rachats, actifs nets, et une API REST pour publier
et lire ces données. Chaque SGO a ses propres couleurs et son logo ; CGF Gestion (#114B80, #567389, #ACC7DF)
sert d'exemple.

Le simulateur reprend celui du dépôt `Simulateur-d-investissement`, qui peut être supprimé.

## Pages

| Page | Accès | Contenu |
|---|---|---|
| Sociétés de gestion | public | SGO de la plateforme |
| Fonds | public | Dernière VL, performances, volatilité de chaque fonds de la SGO |
| Fiche du fonds | public | Historique des VL (périodes, base 100, export CSV), performances, années civiles, pertes depuis le plus haut, risque |
| Rendement attendu | public | Rendement médian et moyen estimés sur 1, 3, 5 ans ou tout l'historique ; projection en éventail, risque de perte, chance d'atteindre un objectif |
| Simulateur | public | Calcule valeur finale, versement, capital ou durée ; rendement d'un fonds au choix, inflation, phase de retraits |
| Souscriptions et rachats | membres de la SGO | Collecte mensuelle, par type de client, par fonds |
| Actifs nets | membres de la SGO | Encours total et par fonds, évolution sur un an |
| Méthodes | public | Formules et API |

## Lancer en local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py amorcer_demo          # SGO CGF Gestion + data_fcp.xlsx
python manage.py createsuperuser
python manage.py runserver
```

Ajouter une SGO et ses membres dans `/admin/`, puis importer son classeur :

```bash
python manage.py importer_classeur fichier.xlsx --sgo "Nom de la SGO" --creer
```

Le classeur peut contenir les feuilles « Valeurs Liquidatives » et « Actifs Nets » (Date, puis une colonne par fonds)
et « Souscriptions Rachats » (Date, Type de clients, Opérations, FCP, Montant). Un fonds connu sous deux noms se
règle par le champ « alias » du fonds ; l'import signale les noms présents dans une seule feuille.

## API

Lecture publique ; écriture des VL, lecture et écriture des actifs nets et des flux réservées aux membres de la SGO,
avec un jeton (`POST /api/jeton/`, puis `Authorization: Token <jeton>`).

| Méthode | Adresse |
|---|---|
| GET | `/api/sgo/`, `/api/fonds/?sgo=<slug>` |
| GET, POST | `/api/fonds/<id>/vl/` (`?debut=&fin=` ; POST `[{"date", "valeur"}]`) |
| GET | `/api/fonds/<id>/performances/`, `/api/fonds/<id>/rendement-attendu/?annees=3&horizon=5` |
| GET, POST | `/api/fonds/<id>/actifs-nets/`, `/api/fonds/<id>/flux/` |
| POST | `/api/simulation/` |

## Production

Variables : `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`,
`DATABASE_URL` (PostgreSQL). Puis `python manage.py collectstatic` et `gunicorn config.wsgi`. Les fichiers
statiques sont servis par WhiteNoise. Streamlit Cloud ne fait pas tourner Django : Render, Railway ou un serveur.

## Tests

```bash
python manage.py test fonds
```
