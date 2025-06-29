from django import forms

from dcim.models import Location, Site
from ipam.models import IPAddress, VLAN
from netbox.forms import NetBoxModelForm
from tenancy.forms import ContactModelFilterForm, TenancyForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .choices import PlugStatusChoices, PlugTypeChoices
from .models import Plug


class PlugForm(NetBoxModelForm, TenancyForm):
    """
    Formulaire pour la création/modification d'une prise réseau (Plug).
    """
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Bâtiment'
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Local'
    )
    contact = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Personne de contact'
    )
    ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='Adresse IP'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='VLAN'
    )
    comments = CommentField(
        label='Commentaire'
    )

    class Meta:
        model = Plug
        fields = [
            'name', 'site', 'location', 'tenant', 'contact', 'status', 
            'interfaceconfig', 'ip_address', 'vlan', 'legacy_id', 'comments',
        ]
        widgets = {
            'status': forms.Select,
            'interfaceconfig': forms.Select,
        }


class PlugFilterForm(ContactModelFilterForm):
    """
    Formulaire pour filtrer les prises réseau (Plug).
    """
    model = Plug
    field_order = [
        'q', 'name', 'site', 'location', 'tenant', 'contact', 'status', 
        'interfaceconfig', 'vlan', 'legacy_id',
    ]

    name = forms.CharField(
        required=False,
        label='Numéro de la prise'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Bâtiment'
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Local'
    )
    status = forms.MultipleChoiceField(
        choices=add_blank_choice(PlugStatusChoices),
        required=False,
        widget=forms.SelectMultiple,
        label='Statut'
    )
    interfaceconfig = forms.MultipleChoiceField(
        choices=add_blank_choice(PlugTypeChoices),
        required=False,
        widget=forms.SelectMultiple,
        label='Type de configuration'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN'
    )
    legacy_id = forms.IntegerField(
        required=False,
        label='ID ancien système'
    )


class PlugBulkEditForm(NetBoxModelForm):
    """
    Formulaire pour l'édition en masse des prises réseau (Plug).
    """
    pk = forms.ModelMultipleChoiceField(
        queryset=Plug.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Bâtiment'
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Local'
    )
    tenant = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Gestionnaire'
    )
    contact = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Personne de contact'
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PlugStatusChoices),
        required=False,
        widget=forms.Select,
        label='Statut'
    )
    interfaceconfig = forms.ChoiceField(
        choices=add_blank_choice(PlugTypeChoices),
        required=False,
        widget=forms.Select,
        label='Type de configuration'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN'
    )
    comments = CommentField(
        label='Commentaire'
    )

    class Meta:
        nullable_fields = [
            'location', 'contact', 'ip_address', 'vlan', 'comments',
        ]