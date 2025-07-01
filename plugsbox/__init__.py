from netbox.plugins import PluginConfig
from .version import __version__


class PlugsboxConfig(PluginConfig):
    name = 'plugsbox'
    verbose_name = 'Plugsbox - Inventaire des prises'
    description = 'Un plugin pour inventorier les prises réseau du campus.'
    version = __version__
    author = 'Nicolas GHAYE'
    author_email = 'nghaye@gmail.com'
    base_url = 'plugsbox'
    required_settings = []
    default_settings = {}
    menu_items = 'navigation.menu_items'
    template_extensions = 'template_content.template_extensions'


config = PlugsboxConfig