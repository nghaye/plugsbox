import django_filters
from django.db.models import Q

from dcim.models import Device, Interface, Site
from ipam.models import VLAN
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Contact, Tenant
#from utilities.filters import MultiValueCharFilter

from .choices import PlugStatusChoices, PlugTypeChoices
from .models import Plug


class PlugFilterSet(NetBoxModelFilterSet):
    """
    FilterSet pour les prises réseau (Plug).
    """
    q = django_filters.CharFilter(
        method='search',
        label='Recherche',
    )
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Numéro de la prise'
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Bâtiment (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Bâtiment (slug)',
    )
    location = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Local'
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Gestionnaire (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Gestionnaire (slug)',
    )
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label='Contact (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PlugStatusChoices,
        label='Statut'
    )
    interfaceconfig = django_filters.MultipleChoiceFilter(
        choices=PlugTypeChoices,
        label='Type de configuration'
    )
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        label='VLAN (ID)',
    )
    switch_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Switch (ID)',
    )
    switch = django_filters.ModelMultipleChoiceFilter(
        field_name='switch__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Switch (nom)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        label='Interface (ID)',
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label='Interface (nom)',
    )
    activation_date = django_filters.DateFilter(
        label="Date d'activation souhaitée"
    )
    legacy_id = django_filters.NumberFilter(
        label='ID ancien système'
    )

    class Meta:
        model = Plug
        fields = [
            'id', 'name', 'site', 'location', 'tenant', 'contact', 
            'status', 'interfaceconfig', 'vlan', 'switch', 'interface', 'activation_date', 'legacy_id',
        ]

    def search(self, queryset, name, value):
        """
        Recherche dans les champs principaux.
        """
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(site__name__icontains=value) |
            Q(location__name__icontains=value) |
            Q(tenant__name__icontains=value) |
            Q(contact__name__icontains=value) |
            Q(switch__name__icontains=value) |
            Q(interface__name__icontains=value) |
            Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)