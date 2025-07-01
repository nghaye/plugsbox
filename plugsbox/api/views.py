from netbox.api.viewsets import NetBoxModelViewSet

from ..models import Plug, Gestionnaire
from ..filtersets import PlugFilterSet, GestionnaireFilterSet
from .serializers import PlugSerializer, GestionnaireSerializer


class PlugViewSet(NetBoxModelViewSet):
    queryset = Plug.objects.select_related(
        'site', 'tenant', 'contact', 'ip_address', 'vlan'
    ).prefetch_related('tags')
    serializer_class = PlugSerializer
    filterset_class = PlugFilterSet


class GestionnaireViewSet(NetBoxModelViewSet):
    queryset = Gestionnaire.objects.select_related(
        'tenant', 'user_group'
    ).prefetch_related('tags')
    serializer_class = GestionnaireSerializer
    filterset_class = GestionnaireFilterSet