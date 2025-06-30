from django.db import models
from django.urls import reverse

from dcim.models import CableTermination, Site
from ipam.models import IPAddress, VLAN
from netbox.models import NetBoxModel
from tenancy.models import Contact, Tenant

from .choices import PlugStatusChoices, PlugTypeChoices


class Plug(CableTermination, NetBoxModel):
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
        if self.location:
            return f"{self.site.name} / {self.location.name} / {self.name}"
        return f"{self.site.name} / {self.name}"

    def get_absolute_url(self):
        return reverse('plugins:plugsbox:plug', args=[self.pk])