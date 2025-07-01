from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.models import Group

from netbox.views import generic
from tenancy.models import Tenant
from extras.models import Tag

from .models import Plug, Gestionnaire
from .forms import PlugForm, PlugFilterForm, PlugBulkEditForm, GestionnaireForm
from .tables import PlugTable, GestionnaireTable
from .filtersets import PlugFilterSet, GestionnaireFilterSet


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

    def get_object(self, **kwargs):
        """Override pour les nouvelles créations"""
        return None

    def form_valid(self, form):
        """Override pour créer automatiquement tenant et user group"""
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        
        # Slugifier le nom
        slug_name = slugify(name)
        
        # Créer ou récupérer le tag "plugsbox"
        plugsbox_tag, created = Tag.objects.get_or_create(
            name='plugsbox',
            defaults={
                'slug': 'plugsbox',
                'description': 'Tag pour les objets créés par Plugsbox'
            }
        )
        
        # Créer le tenant s'il n'existe pas
        tenant, tenant_created = Tenant.objects.get_or_create(
            slug=slug_name,
            defaults={
                'name': name,
                'description': description
            }
        )
        
        # Ajouter le tag au tenant
        if tenant_created:
            tenant.tags.add(plugsbox_tag)
        
        # Créer le user group s'il n'existe pas
        user_group, group_created = Group.objects.get_or_create(
            name=name,
            defaults={}
        )
        
        # Créer l'instance du gestionnaire
        form.instance.name = slug_name
        form.instance.tenant = tenant
        form.instance.user_group = user_group
        
        # Messages informatifs
        if tenant_created:
            messages.success(self.request, f"Tenant '{name}' créé avec succès.")
        else:
            messages.info(self.request, f"Tenant '{name}' existait déjà.")
            
        if group_created:
            messages.success(self.request, f"Groupe d'utilisateurs '{name}' créé avec succès.")
        else:
            messages.info(self.request, f"Groupe d'utilisateurs '{name}' existait déjà.")
        
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