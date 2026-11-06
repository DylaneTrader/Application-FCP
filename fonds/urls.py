from django.urls import path

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("a-propos/", views.a_propos, name="a_propos"),
    path("sgo/<slug:sgo>/", views.tableau_sgo, name="sgo"),
    path("sgo/<slug:sgo>/simulateur/", views.simulateur, name="simulateur"),
    path("sgo/<slug:sgo>/souscriptions-rachats/", views.flux, name="flux"),
    path("sgo/<slug:sgo>/actifs-nets/", views.actifs_nets, name="actifs_nets"),
    path("sgo/<slug:sgo>/fonds/<slug:fonds>/", views.fiche_fonds, name="fonds"),
    path("sgo/<slug:sgo>/fonds/<slug:fonds>/rendement-attendu/", views.rendement_attendu, name="rendement"),
]
