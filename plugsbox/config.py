from netbox.plugins import PluginConfig
from .version import __version__

class PlugsboxConfig(PluginConfig):
    name = 'plugsbox'
    verbose_name = 'Plugsbox - Inventaire des prises'
    description = 'Un plugin pour inventorier les prises réseau du campus.'
    version = __version__
    author = 'Votre Nom'
    author_email = 'votre.email@example.com'
    base_url = 'plugsbox'
    required_settings = []
    default_settings = {}
    menu_items = 'plugsbox.navigation.menu_items'