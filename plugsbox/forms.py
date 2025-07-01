from django import forms

from dcim.models import Device, Interface, Site
from ipam.models import IPAddress, VLAN
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm
from tenancy.models import Contact, Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .choices import PlugStatusChoices, PlugTypeChoices
from .models import Plug, Gestionnaire


class PlugForm(NetBoxModelForm):
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
    # Champs IP visibles seulement en configuration static
    ip_address_static = forms.CharField(
        max_length=15,
        required=False,
        label='Adresse IP',
        help_text='Adresse IP seule (ex: 192.168.1.10)',
        widget=forms.TextInput(attrs={'placeholder': '192.168.1.10', 'class': 'static-only-field'})
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False,
        label='Nom DNS',
        help_text='Nom DNS pour l\'adresse IP',
        widget=forms.TextInput(attrs={'placeholder': 'pc-01.example.com', 'class': 'static-only-field'})
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
            'site_id': '$site',
            'role': 'access'
        },
        label='Switch'
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.filter(cable__isnull=True),
        required=False,
        query_params={
            'device_id': '$switch',
            'cabled': 'false'
        },
        label='Interface'
    )
    related_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        label='Device associé',
        help_text='Device connecté au répartiteur (ex: access point)'
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
            'interfaceconfig', 'vlan', 'switch', 'interface', 'related_device', 'activation_date', 'comments',
        ]
        widgets = {
            'status': forms.Select,
            'interfaceconfig': forms.Select,
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
            
        interfaceconfig = cleaned_data.get('interfaceconfig')
        ip_address_static = cleaned_data.get('ip_address_static')
        
        # Vérifier que l'adresse IP n'est fournie que pour la configuration static
        if ip_address_static and interfaceconfig != 'static':
            raise forms.ValidationError(
                "L'adresse IP ne peut être définie que pour la configuration 'Static'."
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Si une adresse IP est fournie pour la configuration static, la créer
        ip_address_static = self.cleaned_data.get('ip_address_static')
        dns_name = self.cleaned_data.get('dns_name')
        
        if ip_address_static:
            from netaddr import IPAddress as NetAddrIP
            
            try:
                # Valider le format de l'adresse IP et ajouter /32
                ip_addr = NetAddrIP(ip_address_static)
                ip_with_prefix = f"{ip_addr}/32"
                
                # Créer l'objet IPAddress avec le tenant du gestionnaire
                gestionnaire = instance.gestionnaire
                tenant = gestionnaire.tenant if gestionnaire else None
                
                ip_obj = IPAddress(
                    address=ip_with_prefix,
                    dns_name=dns_name or '',
                    status='active',
                    tenant=tenant
                )
                
                if commit:
                    ip_obj.save()
                    instance.ip_address = ip_obj
            except Exception as e:
                raise forms.ValidationError(f"Erreur lors de la création de l'adresse IP: {e}")
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

    class Media:
        js = ('plugsbox/js/plug_form.js',)


class PlugFilterForm(NetBoxModelFilterSetForm):
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
    gestionnaire = DynamicModelChoiceField(
        queryset=Gestionnaire.objects.all(),
        required=False,
        label='Gestionnaire'
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label='Contact'
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
        label='ID Plugs'
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
        max_length=100,
        label='Description',
        help_text="Description du gestionnaire"
    )

    class Meta:
        model = Gestionnaire
        fields = ['name', 'description']