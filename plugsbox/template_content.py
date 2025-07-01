from netbox.plugins import PluginTemplateExtension
from dcim.models import Device


class DevicePlugsExtension(PluginTemplateExtension):
    """Extension pour ajouter du contenu à la vue Device"""
    
    model = 'dcim.device'
    
    def full_width_page(self):
        """Contenu pleine largeur pour afficher les prises"""
        return self.render('dcim/device/plugs.html')


# Enregistrement des extensions
template_extensions = [DevicePlugsExtension]