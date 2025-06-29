import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from .models import Plug


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
        linkify=True,
        verbose_name='Local'
    )
    status = columns.ChoiceFieldColumn(
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
        verbose_name='ID ancien système'
    )
    comments = columns.MarkdownColumn(
        verbose_name='Commentaire'
    )
    
    class Meta(NetBoxTable.Meta):
        model = Plug
        fields = (
            'pk', 'id', 'name', 'site', 'location', 'tenant', 'contact', 'status', 
            'interfaceconfig', 'ip_address', 'vlan', 'legacy_id', 'comments', 
            'created', 'last_updated',
        )
        default_columns = (
            'name', 'site', 'location', 'tenant', 'status', 'interfaceconfig', 
            'ip_address', 'vlan',
        )