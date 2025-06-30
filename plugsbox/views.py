from django.shortcuts import get_object_or_404
from django.db.models import Q

from netbox.views import generic

from .models import Plug
from .forms import PlugForm, PlugFilterForm, PlugBulkEditForm
from .tables import PlugTable
from .filtersets import PlugFilterSet


class PlugListView(generic.ObjectListView):
    """
    Vue pour l'affichage de la liste des prises réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'location', 'tenant', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    filterset_form = PlugFilterForm
    table = PlugTable


class PlugView(generic.ObjectView):
    """
    Vue pour l'affichage du détail d'une prise réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'location', 'tenant', 'contact', 'ip_address', 'vlan'
    )

    def get_extra_context(self, request, instance):
        """
        Ajoute des données supplémentaires au contexte.
        """
        context = super().get_extra_context(request, instance)
        
        # Informations de connexion si disponibles
        if hasattr(instance, 'link_peers'):
            context['link_peers'] = instance.link_peers
        
        return context


class PlugEditView(generic.ObjectEditView):
    """
    Vue pour la création/modification d'une prise réseau.
    """
    queryset = Plug.objects.all()
    form = PlugForm
    template_name = 'plugsbox/plug_edit.html'


class PlugDeleteView(generic.ObjectDeleteView):
    """
    Vue pour la suppression d'une prise réseau.
    """
    queryset = Plug.objects.all()


class PlugBulkImportView(generic.BulkImportView):
    """
    Vue pour l'import en masse des prises réseau.
    """
    queryset = Plug.objects.all()
    model_form = PlugForm


class PlugBulkEditView(generic.BulkEditView):
    """
    Vue pour l'édition en masse des prises réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'location', 'tenant', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    table = PlugTable
    form = PlugBulkEditForm


class PlugBulkDeleteView(generic.BulkDeleteView):
    """
    Vue pour la suppression en masse des prises réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'location', 'tenant', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    table = PlugTable