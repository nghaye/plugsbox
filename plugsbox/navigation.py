from extras.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:plugsbox:plug_list',
        link_text='Prises Réseau',
        permissions=['plugsbox.view_plug'],
        buttons=(
            PluginMenuItem(
                link='plugins:plugsbox:plug_add',
                link_text='Ajouter',
                permissions=['plugsbox.add_plug'],
            ),
            PluginMenuItem(
                link='plugins:plugsbox:plug_import',
                link_text='Importer',
                permissions=['plugsbox.add_plug'],
            ),
        )
    ),
)