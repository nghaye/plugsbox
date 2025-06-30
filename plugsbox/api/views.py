from netbox.api.viewsets import NetBoxModelViewSet

from ..models import Plug
from ..filtersets import PlugFilterSet
from .serializers import PlugSerializer


class PlugViewSet(NetBoxModelViewSet):
    queryset = Plug.objects.select_related(
        'site', 'tenant', 'contact', 'ip_address', 'vlan'
    ).prefetch_related('tags')
    serializer_class = PlugSerializer
    filterset_class = PlugFilterSet