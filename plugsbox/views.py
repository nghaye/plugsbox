from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views.generic import TemplateView

from netbox.views import generic
from tenancy.models import Tenant
from extras.models import Tag

from .models import Plug, Gestionnaire
from .forms import PlugForm, PlugFilterForm, PlugBulkEditForm, GestionnaireForm
from .tables import PlugTable, GestionnaireTable
from .filtersets import PlugFilterSet, GestionnaireFilterSet
from .choices import PlugStatusChoices, PlugTypeChoices


class PlugListView(generic.ObjectListView):
    """
    Vue pour l'affichage de la liste des prises réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'gestionnaire', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    filterset_form = PlugFilterForm
    table = PlugTable


class PlugView(generic.ObjectView):
    """
    Vue pour l'affichage du détail d'une prise réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'gestionnaire', 'contact', 'ip_address', 'vlan'
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
        'site', 'gestionnaire', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    table = PlugTable
    form = PlugBulkEditForm


class PlugBulkDeleteView(generic.BulkDeleteView):
    """
    Vue pour la suppression en masse des prises réseau.
    """
    queryset = Plug.objects.prefetch_related(
        'site', 'gestionnaire', 'contact', 'ip_address', 'vlan'
    )
    filterset = PlugFilterSet
    table = PlugTable


class GestionnaireListView(generic.ObjectListView):
    """
    Vue pour l'affichage de la liste des gestionnaires.
    """
    queryset = Gestionnaire.objects.prefetch_related('tenant', 'user_group')
    filterset = GestionnaireFilterSet
    table = GestionnaireTable


class GestionnaireView(generic.ObjectView):
    """
    Vue pour l'affichage du détail d'un gestionnaire.
    """
    queryset = Gestionnaire.objects.prefetch_related('tenant', 'user_group')


class GestionnaireCreateView(generic.ObjectEditView):
    """
    Vue pour la création d'un gestionnaire avec création automatique du tenant et user group.
    """
    queryset = Gestionnaire.objects.all()
    form = GestionnaireForm
    template_name = 'plugsbox/gestionnaire_edit.html'

    def form_valid(self, form):
        """Override pour slugifier le nom"""
        name = form.cleaned_data['name']
        
        # Slugifier le nom
        slug_name = slugify(name)
        form.instance.name = slug_name
        
        return super().form_valid(form)


class GestionnaireEditView(generic.ObjectEditView):
    """
    Vue pour la modification d'un gestionnaire.
    """
    queryset = Gestionnaire.objects.all()
    form = GestionnaireForm
    template_name = 'plugsbox/gestionnaire_edit.html'


class GestionnaireDeleteView(generic.ObjectDeleteView):
    """
    Vue pour la suppression d'un gestionnaire (ne supprime pas tenant/group).
    """
    queryset = Gestionnaire.objects.all()


class HomeView(TemplateView):
    """
    Vue d'accueil dynamique du plugin Plugsbox.
    Affiche des raccourcis et statistiques basés sur le gestionnaire de l'utilisateur.
    """
    template_name = 'plugsbox/home.html'
    
    def get_user_gestionnaire(self, user):
        """
        Trouve le gestionnaire associé à l'utilisateur basé sur ses groupes.
        """
        if not user.is_authenticated:
            return None
            
        user_groups = user.groups.all()
        for group in user_groups:
            try:
                gestionnaire = Gestionnaire.objects.get(user_group=group)
                return gestionnaire
            except Gestionnaire.DoesNotExist:
                continue
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Détecter le gestionnaire de l'utilisateur
        gestionnaire = self.get_user_gestionnaire(self.request.user)
        context['gestionnaire'] = gestionnaire
        
        if gestionnaire:
            # Requête de base pour les prises du gestionnaire
            plugs_queryset = Plug.objects.filter(gestionnaire=gestionnaire)
            
            # Statistiques
            context['stats'] = {
                'total': plugs_queryset.count(),
                'operational': plugs_queryset.filter(status=PlugStatusChoices.STATUS_OPERATIONAL).count(),
                'to_configure': plugs_queryset.filter(status=PlugStatusChoices.STATUS_TO_CONFIGURE).count(),
                'mab_count': plugs_queryset.filter(interfaceconfig=PlugTypeChoices.TYPE_MAB).count(),
                'pending': plugs_queryset.exclude(
                    status__in=[PlugStatusChoices.STATUS_OPERATIONAL, PlugStatusChoices.STATUS_DELETED]
                ).count()
            }
            
            # 10 dernières prises modifiées
            context['recent_plugs'] = plugs_queryset.order_by('-last_updated')[:10]
            
        else:
            context['stats'] = {
                'total': 0,
                'operational': 0,
                'to_configure': 0,
                'mab_count': 0,
                'pending': 0
            }
            context['recent_plugs'] = []
        
        return context