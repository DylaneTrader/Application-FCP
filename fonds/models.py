"""Une plateforme, plusieurs sociétés de gestion (SGO), chacune avec ses fonds et ses couleurs."""
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

couleur_hex = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Couleur au format #RRVVBB.")

PAYS_UEMOA = [(p, p) for p in ("Bénin", "Burkina Faso", "Côte d'Ivoire", "Guinée-Bissau", "Mali", "Niger",
                               "Sénégal", "Togo")]


class SGO(models.Model):
    """Société de gestion d'OPCVM. Ses membres gèrent ses données ; ses couleurs habillent ses pages."""
    nom = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    pays = models.CharField(max_length=40, choices=PAYS_UEMOA, default="Sénégal")
    site_web = models.URLField(blank=True)
    logo = models.FileField(upload_to="logos/", blank=True,
                            help_text="Logo affiché dans l'en-tête des pages de la SGO.")
    logo_statique = models.CharField(max_length=200, blank=True,
                                     help_text="Chemin d'un logo livré avec l'application (static), si aucun fichier.")
    couleur_primaire = models.CharField(max_length=7, default="#114B80", validators=[couleur_hex])
    couleur_secondaire = models.CharField(max_length=7, default="#567389", validators=[couleur_hex])
    couleur_accent = models.CharField(max_length=7, default="#ACC7DF", validators=[couleur_hex])
    taux_sans_risque = models.FloatField(default=0.03, help_text="Annuel, en décimal (0,03 = 3 %).")
    membres = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="sgos")

    class Meta:
        ordering = ["nom"]
        verbose_name = "SGO"
        verbose_name_plural = "SGO"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("sgo", args=[self.slug])

    def est_membre(self, utilisateur) -> bool:
        if not utilisateur.is_authenticated:
            return False
        return utilisateur.is_superuser or self.membres.filter(pk=utilisateur.pk).exists()


class Fonds(models.Model):
    class Categorie(models.TextChoices):
        MONETAIRE = "monetaire", "Monétaire"
        OBLIGATAIRE = "obligataire", "Obligataire"
        DIVERSIFIE = "diversifie", "Diversifié"
        ACTIONS = "actions", "Actions"
        EPARGNE_SALARIALE = "fcpe", "Épargne salariale (FCPE)"
        CAPITAL_RISQUE = "fcpr", "Capital-risque (FCPR)"
        AUTRE = "autre", "Autre"

    sgo = models.ForeignKey(SGO, on_delete=models.CASCADE, related_name="fonds")
    nom = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True)
    categorie = models.CharField(max_length=20, choices=Categorie.choices, default=Categorie.AUTRE)
    devise = models.CharField(max_length=10, default="FCFA")
    alias = models.TextField(blank=True, help_text="Autres noms du fonds dans les fichiers importés, un par ligne.")
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]
        verbose_name_plural = "fonds"
        constraints = [models.UniqueConstraint(fields=["sgo", "slug"], name="fonds_slug_unique_par_sgo"),
                       models.UniqueConstraint(fields=["sgo", "nom"], name="fonds_nom_unique_par_sgo")]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("fonds", args=[self.sgo.slug, self.slug])

    def noms_connus(self) -> set[str]:
        return {self.nom, *(a.strip() for a in self.alias.splitlines() if a.strip())}


class ValeurLiquidative(models.Model):
    fonds = models.ForeignKey(Fonds, on_delete=models.CASCADE, related_name="vls")
    date = models.DateField()
    valeur = models.FloatField()

    class Meta:
        ordering = ["date"]
        verbose_name = "valeur liquidative"
        constraints = [models.UniqueConstraint(fields=["fonds", "date"], name="vl_unique"),
                       models.CheckConstraint(condition=models.Q(valeur__gt=0), name="vl_positive")]


class ActifNet(models.Model):
    fonds = models.ForeignKey(Fonds, on_delete=models.CASCADE, related_name="actifs_nets")
    date = models.DateField()
    montant = models.FloatField()

    class Meta:
        ordering = ["date"]
        verbose_name = "actif net"
        constraints = [models.UniqueConstraint(fields=["fonds", "date"], name="actif_net_unique")]


class Flux(models.Model):
    class Sens(models.TextChoices):
        SOUSCRIPTION = "S", "Souscription"
        RACHAT = "R", "Rachat"

    fonds = models.ForeignKey(Fonds, on_delete=models.CASCADE, related_name="flux")
    date = models.DateField()
    sens = models.CharField(max_length=1, choices=Sens.choices)
    type_client = models.CharField(max_length=80, blank=True)
    montant = models.FloatField()

    class Meta:
        ordering = ["date"]
        verbose_name = "souscription ou rachat"
        verbose_name_plural = "souscriptions et rachats"
        indexes = [models.Index(fields=["fonds", "date"])]
