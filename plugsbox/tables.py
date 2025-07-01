import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from .models import Plug, Gestionnaire


class PlugTable(NetBoxTable, TenancyColumnsMixin, ContactsColumnMixin):
    """
    Table pour l'affichage des prises réseau (Plug).
    """
    name = tables.Column(
        linkify=True,
        verbose_name='Numéro de la prise'
    )
    site = tables.Column(
        linkify=True,
        verbose_name='Bâtiment'
    )
    location = tables.Column(
        verbose_name='Local'
    )
    gestionnaire = tables.Column(
        linkify=True,
        verbose_name='Gestionnaire'
    )
    status = columns.TemplateColumn(
        template_code='<span class="badge bg-{{ record.get_status_color }}">{{ record.get_status_display }}</span>',
        verbose_name='Statut'
    )
    interfaceconfig = columns.ChoiceFieldColumn(
        verbose_name='Type de configuration'
    )
    ip_address = tables.Column(
        linkify=True,
        verbose_name='Adresse IP'
    )
    vlan = tables.Column(
        linkify=True,
        verbose_name='VLAN'
    )
    legacy_id = tables.Column(
        verbose_name='ID Plugs'
    )
    contact = tables.Column(
        linkify=True,
        verbose_name='Contact'
    )
    activation_date = tables.DateColumn(
        verbose_name="Activation Souhaitée"
    )
    switch = tables.Column(
        linkify=True,
        verbose_name='Switch'
    )
    interface = tables.Column(
        linkify=True,
        verbose_name='Interface'
    )
    patch_panel_plug = tables.Column(
        linkify=True,
        verbose_name='Port répartiteur'
    )
    related_device = tables.Column(
        linkify=True,
        verbose_name='Device associé'
    )
    comments = columns.MarkdownColumn(
        verbose_name='Commentaire'
    )
    
    class Meta(NetBoxTable.Meta):
        model = Plug
        fields = (
            'pk', 'id', 'name', 'site', 'location', 'gestionnaire', 'contact', 'status', 
            'interfaceconfig', 'ip_address', 'vlan', 'switch', 'interface', 'patch_panel_plug', 'related_device', 'activation_date', 'legacy_id', 'comments', 
            'created', 'last_updated',
        )
        default_columns = (
            'name', 'site', 'location', 'gestionnaire', 'contact', 'status', 'interfaceconfig', 
            'ip_address', 'vlan', 'switch', 'interface', 'activation_date',
        )


class GestionnaireTable(NetBoxTable):
    """
    Table pour l'affichage des gestionnaires.
    """
    name = tables.Column(
        linkify=True,
        verbose_name='Nom'
    )
    description = tables.Column(
        verbose_name='Description'
    )
    tenant = tables.Column(
        linkify=True,
        verbose_name='Tenant'
    )
    user_group = tables.Column(
        verbose_name='Groupe d\'utilisateurs'
    )
    plug_count = tables.Column(
        accessor='plugs__count',
        verbose_name='Nombre de prises',
        orderable=False
    )
    
    class Meta(NetBoxTable.Meta):
        model = Gestionnaire
        fields = (
            'pk', 'id', 'name', 'description', 'tenant', 'user_group', 'plug_count',
            'created', 'last_updated',
        )
        default_columns = (
            'name', 'description', 'tenant', 'user_group', 'plug_count',
        )