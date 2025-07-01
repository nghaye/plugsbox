from netbox.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link='plugins:plugsbox:home',
        link_text='Accueil',
        permissions=[]
    ),
    PluginMenuItem(
        link='plugins:plugsbox:plug_list',
        link_text='Prises Réseau',
        permissions=['plugsbox.view_plug'],
        buttons=(
            PluginMenuButton(
                link='plugins:plugsbox:plug_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['plugsbox.add_plug'],
            ),
            PluginMenuButton(
                link='plugins:plugsbox:plug_import',
                title='Importer',
                icon_class='mdi mdi-upload',
                permissions=['plugsbox.add_plug'],
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:plugsbox:gestionnaire_list',
        link_text='Gestionnaires',
        permissions=['plugsbox.view_gestionnaire'],
        buttons=(
            PluginMenuButton(
                link='plugins:plugsbox:gestionnaire_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['plugsbox.add_gestionnaire'],
            ),
        )
    ),
)