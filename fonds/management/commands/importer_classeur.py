from django.core.management.base import BaseCommand, CommandError

from fonds.importation import importer_classeur
from fonds.models import SGO


class Command(BaseCommand):
    help = "Importe les VL, actifs nets et flux d'un classeur Excel (ou un CSV de VL) pour une SGO."

    def add_arguments(self, parser):
        parser.add_argument("chemin")
        parser.add_argument("--sgo", required=True, help="Nom ou slug de la SGO.")
        parser.add_argument("--creer", action="store_true", help="Crée la SGO si elle n'existe pas.")

    def handle(self, chemin, sgo, creer, **_):
        objet = SGO.objects.filter(slug=sgo).first() or SGO.objects.filter(nom__iexact=sgo).first()
        if objet is None:
            if not creer:
                raise CommandError(f"SGO inconnue : {sgo} (ajoutez --creer pour la créer).")
            objet = SGO.objects.create(nom=sgo)
        try:
            rapport = importer_classeur(chemin, objet)
        except (OSError, ValueError) as erreur:
            raise CommandError(str(erreur)) from erreur
        self.stdout.write(self.style.SUCCESS(
            f"{objet} : {rapport.vl} VL, {rapport.actifs} actifs nets, {rapport.flux} flux importés."))
        if rapport.fonds_crees:
            self.stdout.write(f"Fonds créés ({len(rapport.fonds_crees)}) : {', '.join(rapport.fonds_crees)}")
        for titre, noms in rapport.fonds_isoles().items():
            if noms:
                self.stdout.write(self.style.WARNING(f"{titre} : {', '.join(noms)}"))
        if any(rapport.fonds_isoles().values()):
            self.stdout.write("Si ce sont les mêmes fonds sous deux noms, ajoutez l'un en alias de l'autre dans "
                              "l'administration, supprimez le doublon, puis relancez l'import.")
        for ligne in rapport.ignores:
            self.stdout.write(self.style.WARNING(ligne))
