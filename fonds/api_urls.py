from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import api

routeur = DefaultRouter()
routeur.register("sgo", api.SGOViewSet, basename="api-sgo")
routeur.register("fonds", api.FondsViewSet, basename="api-fonds")

urlpatterns = [
    path("", include(routeur.urls)),
    path("simulation/", api.SimulationView.as_view(), name="api-simulation"),
    path("jeton/", obtain_auth_token, name="api-jeton"),
]
