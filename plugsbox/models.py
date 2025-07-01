from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from dcim.models import Cable, Device, DeviceRole, DeviceType, Interface, Manufacturer, Site, FrontPort, RearPort
from ipam.models import IPAddress, VLAN
from netbox.models import NetBoxModel
from tenancy.models import Contact, Tenant
from users.models import Group

from .choices import PlugStatusChoices, PlugTypeChoices


def default_activation_date():
    """Retourne la date par défaut pour l'activation (aujourd'hui + 7 jours)"""
    return date.today() + timedelta(days=7)


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


def get_or_create_patch_panel_manufacturer():
    """Crée ou récupère le fabricant générique pour les répartiteurs"""
    manufacturer, created = Manufacturer.objects.get_or_create(
        name='Generic Patch Panel',
        defaults={
            'slug': 'generic-patch-panel',
            'description': 'Fabricant générique pour les répartiteurs'
        }
    )
    return manufacturer


def get_or_create_patch_panel_device_type():
    """Crée ou récupère le type de device générique pour les répartiteurs"""
    manufacturer = get_or_create_patch_panel_manufacturer()
    device_type, created = DeviceType.objects.get_or_create(
        manufacturer=manufacturer,
        model='Repartiteur',
        defaults={
            'slug': 'repartiteur',
            'description': 'Répartiteur générique',
            'u_height': 1,
            'is_full_depth': False,
        }
    )
    return device_type


def get_patch_panel_name(switch_name, site_name):
    """Détermine le nom du répartiteur selon la logique définie"""
    if len(switch_name) >= 4:
        # Vérifier si le caractère -2 est 'a' ou 'w' et le caractère -1 est un chiffre
        if switch_name[-2] in ['a', 'w'] and switch_name[-1].isdigit():
            # Le caractère -3 est l'id du répartiteur
            repartiteur_id = switch_name[-3]
            # La substring [0,-4] est le nom du bâtiment
            batiment_name = switch_name[:-3]
            return f"{batiment_name}-{repartiteur_id}"
    
    # Sinon prendre juste le nom du bâtiment
    return site_name


def get_or_create_patch_panel_device(switch_name, site):
    """Crée ou récupère le device répartiteur pour un switch donné"""
    device_type = get_or_create_patch_panel_device_type()
    device_role = get_or_create_passive_device_role()
    
    patch_panel_name = get_patch_panel_name(switch_name, site.slug)
    
    device, created = Device.objects.get_or_create(
        name=patch_panel_name,
        site=site,
        defaults={
            'device_type': device_type,
            'role': device_role,
            'status': 'active',
            'comments': f'Répartiteur pour les prises du site {patch_panel_name}'
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
    # Front port côté utilisateur pour le câble
    patch_panel_plug = models.OneToOneField(
        to=FrontPort,
        on_delete=models.CASCADE,
        related_name='plug_user_side',
        blank=True,
        null=True,
        verbose_name="Front port répartiteur",
        help_text="Front port du répartiteur représentant la prise côté utilisateur"
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
    # Device associé (ex: access point)
    related_device = models.ForeignKey(
        to=Device,
        on_delete=models.SET_NULL,
        related_name='related_plugs',
        blank=True,
        null=True,
        verbose_name="Device associé",
        help_text="Device connecté au répartiteur (ex: access point)"
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

    def _create_patch_panel_plug(self):
        """Crée un front port sur le répartiteur pour la prise"""
        if not self.patch_panel_plug and self.site and self.switch:
            # Récupérer ou créer le device répartiteur pour ce switch
            patch_panel_device = get_or_create_patch_panel_device(self.switch.name, self.site)
            
            # Créer d'abord un rear port (obligatoire pour le front port)
            rear_port, _ = RearPort.objects.get_or_create(
                device=patch_panel_device,
                name=f"{self.name}_rear",
                defaults={
                    'type': '8p8c',
                    'positions': 1,
                    'description': f"Port arrière pour prise {self.name}"
                }
            )
            
            # Connecter le rear port au related_device si spécifié
            if self.related_device:
                self._connect_rear_port_to_device(rear_port)
            
            # Créer le front port associé au rear port
            patch_panel_plug = FrontPort.objects.create(
                device=patch_panel_device,
                name=f"{self.name}",
                type='8p8c',  # Type RJ45 par défaut
                rear_port=rear_port,
                rear_port_position=1,
                description=f"Port répartiteur pour prise {self.name} - {self.site.name}"
            )
            self.patch_panel_plug = patch_panel_plug
            return patch_panel_plug
        return self.patch_panel_plug

    def _connect_rear_port_to_device(self, rear_port):
        """Connecte le rear port au related_device via l'interface Ethernet avec l'ID le plus faible"""
        if self.related_device:
            # Trouver l'interface Ethernet avec l'ID le plus faible
            interface = Interface.objects.filter(
                device=self.related_device,
                type__icontains='base-t'
            ).order_by('id').first()
            
            if interface:
                # Créer un câble entre le rear port et l'interface du device
                cable = Cable(
                    a_terminations=[rear_port],
                    b_terminations=[interface],
                    label=f"{self.site.slug}-{self.name} vers {self.related_device.name}",
                    type='cat6'
                )
                cable.save()

    def _create_cable(self):
        """Crée un câble entre le front port répartiteur et l'interface switch"""
        if self.interface and self.patch_panel_plug and not self.cable:
            cable = Cable(
                a_terminations=[self.patch_panel_plug],
                b_terminations=[self.interface],
                label=f"{self.site.slug}-{self.name}",
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
        """Supprime le câble et le front port répartiteur si plus d'interface switch"""
        if self.cable:
            self.cable.delete()
            self.cable = None
        # if self.patch_panel_plug:
        #     self.patch_panel_plug.delete()
        #     self.patch_panel_plug = None

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
            self.interface and self.site and self.switch):
            if old_interface != self.interface:
                # Interface nouvelle ou modifiée
                if not self.patch_panel_plug:
                    self._create_patch_panel_plug()
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
    description = models.CharField(
        max_length=100,
        verbose_name="Description",
        help_text="Description du gestionnaire"
    )
    tenant = models.OneToOneField(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='gestionnaire',
        blank=True,
        null=True,
        verbose_name="Tenant"
    )
    user_group = models.OneToOneField(
        to=Group,
        on_delete=models.PROTECT,
        related_name='gestionnaire',
        blank=True,
        null=True,
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
    
    def save(self, *args, **kwargs):
        """Override save pour créer automatiquement tenant et user_group"""
        # Sauvegarder d'abord l'objet pour avoir un ID
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Si c'est un nouvel objet et qu'il n'a pas encore de tenant/user_group
        if is_new and (not self.tenant or not self.user_group):
            self._create_associated_objects()
    
    def _create_associated_objects(self):
        """Crée les objets Tenant et UserGroup associés si ils n'existent pas"""
        from tenancy.models import Tenant
        from users.models import Group
        from extras.models import Tag
        
        # Créer ou récupérer le tag "plugsbox"
        plugsbox_tag, _ = Tag.objects.get_or_create(
            name='plugsbox',
            defaults={
                'slug': 'plugsbox',
                'description': 'Tag pour les objets créés par Plugsbox'
            }
        )
        
        # Créer le tenant s'il n'existe pas
        if not self.tenant:
            tenant, tenant_created = Tenant.objects.get_or_create(
                slug=self.name,
                defaults={
                    'name': self.name,
                    'description': self.description
                }
            )
            
            # Ajouter le tag au tenant
            if tenant_created:
                tenant.tags.add(plugsbox_tag)
            
            self.tenant = tenant
        
        # Créer le user group s'il n'existe pas
        if not self.user_group:
            user_group, _ = Group.objects.get_or_create(
                name=self.name,
                defaults={}
            )
            self.user_group = user_group
        
        # Sauvegarder à nouveau avec les objets associés
        if self.tenant or self.user_group:
            super().save(update_fields=['tenant', 'user_group'])

