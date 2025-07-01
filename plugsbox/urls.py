from django.urls import path
from . import views

app_name = 'plugsbox'

urlpatterns = [
    # Liste des prises
    path('plugs/', views.PlugListView.as_view(), name='plug_list'),
    
    # Détail d'une prise
    path('plugs/<int:pk>/', views.PlugView.as_view(), name='plug'),
    
    # Création/édition d'une prise
    path('plugs/add/', views.PlugEditView.as_view(), name='plug_add'),
    path('plugs/<int:pk>/edit/', views.PlugEditView.as_view(), name='plug_edit'),
    
    # Suppression d'une prise
    path('plugs/<int:pk>/delete/', views.PlugDeleteView.as_view(), name='plug_delete'),
    
    # Import en masse
    path('plugs/import/', views.PlugBulkImportView.as_view(), name='plug_import'),
    
    # Édition en masse
    path('plugs/edit/', views.PlugBulkEditView.as_view(), name='plug_bulk_edit'),
    
    # Suppression en masse
    path('plugs/delete/', views.PlugBulkDeleteView.as_view(), name='plug_bulk_delete'),
    
    # Changelog
    path('plugs/<int:pk>/changelog/', views.PlugView.as_view(), name='plug_changelog'),
    
    # Gestionnaires
    path('gestionnaires/', views.GestionnaireListView.as_view(), name='gestionnaire_list'),
    path('gestionnaires/<int:pk>/', views.GestionnaireView.as_view(), name='gestionnaire'),
    path('gestionnaires/add/', views.GestionnaireCreateView.as_view(), name='gestionnaire_add'),
    path('gestionnaires/<int:pk>/edit/', views.GestionnaireEditView.as_view(), name='gestionnaire_edit'),
    path('gestionnaires/<int:pk>/delete/', views.GestionnaireDeleteView.as_view(), name='gestionnaire_delete'),
    path('gestionnaires/<int:pk>/changelog/', views.GestionnaireView.as_view(), name='gestionnaire_changelog'),
]