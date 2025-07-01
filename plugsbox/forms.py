from django import forms

from dcim.models import Device, Interface, Site
from ipam.models import IPAddress, VLAN
from netbox.forms import NetBoxModelForm
from tenancy.forms import ContactModelFilterForm, TenancyForm
from tenancy.models import Contact, Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .choices import PlugStatusChoices, PlugTypeChoices
from .models import Plug, Gestionnaire


class PlugForm(NetBoxModelForm, TenancyForm):
    """
    Formulaire pour la création/modification d'une prise réseau (Plug).
    """
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Bâtiment'
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        label='Local'
    )
    gestionnaire = DynamicModelChoiceField(
        queryset=Gestionnaire.objects.all(),
        required=True,
        label='Gestionnaire'
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label='Personne de contact'
    )
    interfaceconfig = forms.ChoiceField(
        choices=PlugTypeChoices,
        label='Configuration'
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
    switch = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Switch'
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$switch'
        },
        label='Interface'
    )
    activation_date = forms.DateField(
        required=False,
        label="Date d'activation souhaitée",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    comments = CommentField(
        label='Commentaire'
    )

    class Meta:
        model = Plug
        fields = [
            'name', 'site', 'location', 'gestionnaire', 'contact', 'status', 
            'interfaceconfig', 'ip_address', 'vlan', 'switch', 'interface', 'activation_date', 'comments',
        ]
        widgets = {
            'status': forms.Select,
            'interfaceconfig': forms.Select,
        }

    class Media:
        js = ('plugsbox/js/plug_form.js',)


class PlugFilterForm(ContactModelFilterForm):
    """
    Formulaire pour filtrer les prises réseau (Plug).
    """
    model = Plug
    field_order = [
        'q', 'name', 'site', 'location', 'gestionnaire', 'contact', 'status', 
        'interfaceconfig', 'vlan', 'switch', 'interface', 'activation_date', 'legacy_id',
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
    location = forms.CharField(
        max_length=200,
        required=False,
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
    activation_date = forms.DateField(
        required=False,
        label="Date d'activation souhaitée",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    switch = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Switch'
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Interface'
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
    location = forms.CharField(
        max_length=200,
        required=False,
        label='Local'
    )
    gestionnaire = DynamicModelChoiceField(
        queryset=Gestionnaire.objects.all(),
        required=False,
        label='Gestionnaire'
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
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
    activation_date = forms.DateField(
        required=False,
        label="Date d'activation souhaitée",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    switch = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Switch'
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Interface'
    )
    comments = CommentField(
        label='Commentaire'
    )

    class Meta:
        nullable_fields = [
            'location', 'contact', 'ip_address', 'vlan', 'switch', 'interface', 'activation_date', 'comments',
        ]


class GestionnaireForm(NetBoxModelForm):
    """
    Formulaire pour la création/modification d'un gestionnaire.
    """
    name = forms.CharField(
        max_length=100,
        label='Nom',
        help_text="Nom du gestionnaire (sera sluggifié automatiquement)"
    )
    description = forms.CharField(
        widget=forms.Textarea,
        label='Description',
        help_text="Description du gestionnaire"
    )

    class Meta:
        model = Gestionnaire
        fields = ['name', 'description']