from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from fonds.models import SGO


class Command(BaseCommand):
    help = "Crée la SGO CGF Gestion (couleurs et logo) et importe le classeur d'exemple data_fcp.xlsx."

    def handle(self, **_):
        sgo, cree = SGO.objects.get_or_create(
            slug="cgf-gestion",
            defaults=dict(nom="CGF Gestion", pays="Sénégal", logo_statique="fonds/logos/cgf-gestion.png", couleur_primaire="#114B80",
                          couleur_secondaire="#567389", couleur_accent="#ACC7DF"))
        self.stdout.write(f"SGO {'créée' if cree else 'existante'} : {sgo}")
        call_command("importer_classeur", str(Path(settings.BASE_DIR) / "data_fcp.xlsx"), sgo=sgo.slug,
                     stdout=self.stdout)
