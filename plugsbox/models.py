from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from dcim.models import Cable, Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import IPAddress, VLAN
from netbox.models import NetBoxModel
from tenancy.models import Contact, Tenant
from users.models import Group

from .choices import PlugStatusChoices, PlugTypeChoices


def default_activation_date():
    """Retourne la date par défaut pour l'activation (aujourd'hui + 7 jours)"""
    return date.today() + timedelta(days=7)


def get_or_create_wall_jacks_manufacturer():
    """Crée ou récupère le fabricant générique pour les prises murales"""
    manufacturer, created = Manufacturer.objects.get_or_create(
        name='Generic Wall Jacks',
        defaults={
            'slug': 'generic-wall-jacks',
            'description': 'Fabricant générique pour les prises réseau murales'
        }
    )
    return manufacturer


def get_or_create_wall_jacks_device_type():
    """Crée ou récupère le type de device générique pour les prises murales"""
    manufacturer = get_or_create_wall_jacks_manufacturer()
    device_type, created = DeviceType.objects.get_or_create(
        manufacturer=manufacturer,
        model='Wall Jacks Panel',
        defaults={
            'slug': 'wall-jacks-panel',
            'description': 'Panneau virtuel pour les prises réseau murales',
            'u_height': 0,  # Pas de hauteur rack
            'is_full_depth': False,
        }
    )
    return device_type


def get_or_create_passive_device_role():
    """Crée ou récupère le rôle de device passif"""
    device_role, created = DeviceRole.objects.get_or_create(
        name='Passif',
        defaults={
            'slug': 'passif',
            'color': 'gray',
            'description': 'Équipement passif (prises murales, panneaux de brassage, etc.)'
        }
    )
    return device_role


def get_or_create_wall_jacks_device(site):
    """Crée ou récupère le device générique pour les prises murales d'un site"""
    device_type = get_or_create_wall_jacks_device_type()
    device_role = get_or_create_passive_device_role()
    device, created = Device.objects.get_or_create(
        name=f'{site.slug}-prises',
        site=site,
        defaults={
            'device_type': device_type,
            'role': device_role,
            'status': 'active',
            'comments': f'Device virtuel pour les prises murales du site {site.name}'
        }
    )
    return device


class Plug(NetBoxModel):
    """
    Représente une prise réseau sur le campus.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Numéro de la prise",
        help_text="Identifiant unique de la prise dans le bâtiment (ex: P-01-123)"
    )
    gestionnaire = models.ForeignKey(
        to='Gestionnaire',
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
    # Interface virtuelle côté utilisateur pour le câble
    user_interface = models.OneToOneField(
        to=Interface,
        on_delete=models.CASCADE,
        related_name='plug_user_side',
        blank=True,
        null=True,
        verbose_name="Interface utilisateur",
        help_text="Interface virtuelle représentant la prise côté utilisateur"
    )
    # Câble entre la prise et le switch
    cable = models.OneToOneField(
        to=Cable,
        on_delete=models.SET_NULL,
        related_name='plug_connection',
        blank=True,
        null=True,
        verbose_name="Câble",
        help_text="Câble connectant la prise au switch"
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

    def _create_user_interface(self):
        """Crée une interface virtuelle côté utilisateur pour la prise"""
        if not self.user_interface and self.site:
            # Récupérer ou créer le device générique pour les prises murales de ce site
            wall_jacks_device = get_or_create_wall_jacks_device(self.site)
            
            # Créer l'interface sur le device générique
            user_interface = Interface.objects.create(
                device=wall_jacks_device,
                name=f"{self.name}",
                type='1000base-t',  # Type par défaut pour une prise réseau
                description=f"Prise murale {self.name} - {self.location}"
            )
            self.user_interface = user_interface
            return user_interface
        return self.user_interface

    def _create_cable(self):
        """Crée un câble entre l'interface utilisateur et l'interface switch"""
        if self.interface and self.user_interface and not self.cable:
            cable = Cable(
                a_terminations=[self.user_interface],
                b_terminations=[self.interface],
                label=f"Câble vers prise {self.name}",
                type='cat6'  # Type par défaut
            )
            cable.save()
            self.cable = cable
            return cable
        return self.cable

    def _update_cable(self, old_interface):
        """Met à jour le câble existant si l'interface change"""
        if self.cable and old_interface != self.interface:
            if self.interface:
                # Supprimer l'ancien câble
                self.cable.delete()
                self.cable = None
                # Créer un nouveau câble avec la nouvelle interface
                self._create_cable()
            else:
                # Supprimer le câble si plus d'interface
                self.cable.delete()
                self.cable = None

    def _cleanup_cable(self):
        """Supprime le câble et l'interface utilisateur si plus d'interface switch"""
        if self.cable:
            self.cable.delete()
            self.cable = None
        if self.user_interface:
            self.user_interface.delete()
            self.user_interface = None

    def save(self, *args, **kwargs):
        """Sauvegarde avec gestion automatique des câbles"""
        # Récupérer l'ancienne interface et l'ancien statut si on modifie un objet existant
        old_interface = None
        old_status = None
        if self.pk:
            try:
                old_instance = Plug.objects.get(pk=self.pk)
                old_interface = old_instance.interface
                old_status = old_instance.status
            except Plug.DoesNotExist:
                pass

        # Vérifier si le statut nécessite la suppression du câble
        status_requiring_cable_cleanup = [
            PlugStatusChoices.STATUS_TO_PATCH,
            PlugStatusChoices.STATUS_DELETED,
            PlugStatusChoices.STATUS_DEFECTIVE
        ]
        
        # Si le statut change vers un statut qui nécessite la suppression du câble
        if (old_status and old_status != self.status and 
            self.status in status_requiring_cable_cleanup):
            # Nettoyer le câble et remettre à null les champs switch/interface
            self._cleanup_cable()
            self.switch = None
            self.interface = None

        # Sauvegarder d'abord l'objet
        super().save(*args, **kwargs)

        # Gérer les câbles selon les cas (seulement si le statut le permet)
        if (self.status not in status_requiring_cable_cleanup and 
            self.interface and self.site):
            if old_interface != self.interface:
                # Interface nouvelle ou modifiée
                if not self.user_interface:
                    self._create_user_interface()
                if old_interface and self.cable:
                    # Mettre à jour le câble existant
                    self._update_cable(old_interface)
                elif not self.cable:
                    # Créer un nouveau câble
                    self._create_cable()
                # Sauvegarder à nouveau pour persister les relations
                super().save(*args, **kwargs)
        elif not self.interface:
            # Plus d'interface, nettoyer les câbles
            if old_interface:
                self._cleanup_cable()
                super().save(*args, **kwargs)

    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Vérifier que l'interface appartient bien au switch sélectionné
        if self.interface and self.switch:
            if self.interface.device != self.switch:
                raise ValidationError({
                    'interface': f"L'interface {self.interface} n'appartient pas au switch {self.switch}"
                })

    def delete(self, *args, **kwargs):
        """Suppression avec nettoyage des câbles"""
        # Nettoyer les câbles et interfaces avant suppression
        self._cleanup_cable()
        super().delete(*args, **kwargs)


class Gestionnaire(NetBoxModel):
    """
    Représente un gestionnaire de prises avec son tenant et user group associés.
    """
    name = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom sluggifié du gestionnaire"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description du gestionnaire"
    )
    tenant = models.OneToOneField(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='gestionnaire',
        verbose_name="Tenant"
    )
    user_group = models.OneToOneField(
        to=Group,
        on_delete=models.PROTECT,
        related_name='gestionnaire',
        verbose_name="Groupe d'utilisateurs"
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Gestionnaire'
        verbose_name_plural = 'Gestionnaires'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:plugsbox:gestionnaire', args=[self.pk])

