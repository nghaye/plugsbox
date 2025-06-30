from datetime import date, timedelta
from django.db import models
from django.urls import reverse

from dcim.models import Device, Interface, Site
from ipam.models import IPAddress, VLAN
from netbox.models import NetBoxModel
from tenancy.models import Contact, Tenant

from .choices import PlugStatusChoices, PlugTypeChoices


def default_activation_date():
    """Retourne la date par défaut pour l'activation (aujourd'hui + 7 jours)"""
    return date.today() + timedelta(days=7)


class Plug(NetBoxModel):
    """
    Représente une prise réseau sur le campus.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Numéro de la prise",
        help_text="Identifiant unique de la prise dans le bâtiment (ex: P-01-123)"
    )
    tenant = models.ForeignKey(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='plugs',
        verbose_name="Gestionnaire"
    )
    contact = models.ForeignKey(
        to=Contact,
        on_delete=models.SET_NULL,
        related_name='plugs',
        blank=True,
        null=True,
        verbose_name="Personne de contact"
    )
    site = models.ForeignKey(
        to=Site,
        on_delete=models.PROTECT,
        related_name='plugs',
        verbose_name="Bâtiment"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Local"
    )
    ip_address = models.OneToOneField(
        to=IPAddress,
        on_delete=models.SET_NULL,
        related_name='plug',
        blank=True,
        null=True,
        verbose_name="Adresse IP"
    )
    interfaceconfig = models.CharField(
        max_length=50,
        choices=PlugTypeChoices,
        default=PlugTypeChoices.TYPE_MAB,
        verbose_name="Type de configuration"
    )
    vlan = models.ForeignKey(
        to=VLAN,
        on_delete=models.SET_NULL,
        related_name='plugs',
        blank=True,
        null=True,
        verbose_name="VLAN"
    )
    comments = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )
    status = models.CharField(
        max_length=50,
        choices=PlugStatusChoices,
        default=PlugStatusChoices.STATUS_TO_PATCH,
        verbose_name="Statut"
    )
    # Ajout de l'ID vers l'ancienne DB Plugs
    legacy_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="ID PLUGS",
        help_text="Identifiant dans l'ancienne base de données Plugs"
    )
    # Date d'activation souhaitée
    activation_date = models.DateField(
        blank=True,
        null=True,
        #default=default_activation_date,
        verbose_name="Date d'activation souhaitée",
        help_text="Date à partir de laquelle la prise devrait être activée"
    )
    # Switch et interface associés
    switch = models.ForeignKey(
        to=Device,
        on_delete=models.SET_NULL,
        related_name='plugs',
        blank=True,
        null=True,
        verbose_name="Switch",
        help_text="Switch auquel la prise est connectée"
    )
    interface = models.ForeignKey(
        to=Interface,
        on_delete=models.SET_NULL,
        related_name='plugs',
        blank=True,
        null=True,
        verbose_name="Interface",
        help_text="Interface du switch à laquelle la prise est connectée"
    )

    class Meta:
        ordering = ('site', 'location', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name'
            ),
        )
        verbose_name = 'Prise'
        verbose_name_plural = 'Prises'

    def __str__(self):
        #if self.location:
        #    return f"{self.site.name} / {self.location} / {self.name}"
        return f"{self.site.name} / {self.name} ({self.interfaceconfig})"

    def get_absolute_url(self):
        return reverse('plugins:plugsbox:plug', args=[self.pk])

    def get_status_color(self):
        """Retourne la couleur Bootstrap pour le statut"""
        color_map = {
            PlugStatusChoices.STATUS_OPERATIONAL: 'success',  # vert
            PlugStatusChoices.STATUS_TO_PATCH: 'warning',     # jaune
            PlugStatusChoices.STATUS_TO_CONFIGURE: 'info',    # bleu
            PlugStatusChoices.STATUS_DEFECTIVE: 'danger',     # rouge
            PlugStatusChoices.STATUS_TO_DELETE: 'secondary',  # gris
            PlugStatusChoices.STATUS_DELETED: 'dark',         # noir
            PlugStatusChoices.STATUS_VERIFY_PATCHING: 'warning',  # jaune
            PlugStatusChoices.STATUS_VERIFY_FLUKE: 'warning',     # jaune
        }
        return color_map.get(self.status, 'secondary')

