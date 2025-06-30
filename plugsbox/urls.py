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
]