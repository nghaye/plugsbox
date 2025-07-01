from rest_framework import serializers

from dcim.api.serializers import DeviceSerializer, InterfaceSerializer, FrontPortSerializer
from dcim.api.serializers_.sites import SiteSerializer
from ipam.api.serializers_.ip import IPAddressSerializer
from ipam.api.serializers_.vlans import VLANSerializer
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.contacts import ContactSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from users.api.serializers import GroupSerializer

from ..models import Plug, Gestionnaire


class GestionnaireSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:plugsbox-api:gestionnaire-detail'
    )
    tenant = TenantSerializer(read_only=True)
    user_group = GroupSerializer(read_only=True)

    class Meta:
        model = Gestionnaire
        fields = [
            'id', 'url', 'display', 'name', 'description', 'tenant', 
            'user_group', 'tags', 'custom_fields', 'created', 'last_updated'
        ]


class NestedGestionnaireSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:plugsbox-api:gestionnaire-detail'
    )

    class Meta:
        model = Gestionnaire
        fields = ['id', 'url', 'display', 'name']


class PlugSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:plugsbox-api:plug-detail'
    )
    site = SiteSerializer(read_only=True)
    gestionnaire = GestionnaireSerializer(read_only=True)
    contact = ContactSerializer(required=False, allow_null=True, read_only=True)
    ip_address = IPAddressSerializer(required=False, allow_null=True, read_only=True)
    vlan = VLANSerializer(required=False, allow_null=True, read_only=True)
    switch = DeviceSerializer(required=False, allow_null=True, read_only=True)
    interface = InterfaceSerializer(required=False, allow_null=True, read_only=True)
    patch_panel_plug = FrontPortSerializer(required=False, allow_null=True, read_only=True)
    related_device = DeviceSerializer(required=False, allow_null=True, read_only=True)

    class Meta:
        model = Plug
        fields = [
            'id', 'url', 'display', 'name', 'site', 'location', 'gestionnaire', 
            'contact', 'status', 'interfaceconfig', 'ip_address', 'vlan', 
            'switch', 'interface', 'patch_panel_plug', 'related_device', 'activation_date', 'legacy_id', 'comments', 'tags', 'custom_fields', 'created', 
            'last_updated'
        ]


class NestedPlugSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:plugsbox-api:plug-detail'
    )

    class Meta:
        model = Plug
        fields = ['id', 'url', 'display', 'name']