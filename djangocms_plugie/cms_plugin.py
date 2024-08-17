from cms.plugin_base import CMSPluginBase, PluginMenuItem
from cms.models import CMSPlugin, PlaceholderReference
from cms.plugin_pool import plugin_pool
from django.urls import reverse
from django.http import HttpRequest
from typing import Literal, List


@plugin_pool.register_plugin
class PlugiePlugin(CMSPluginBase):
    """
    Plugin for importing and exporting plugins.
    
    This plugin adds the ability to import and export plugins and placeholders
    to the plugin and placeholder menus.
    """
    system = True
    render_plugin = False

    def get_extra_plugin_menu_items(request: HttpRequest, plugin: CMSPlugin) -> List[PluginMenuItem]:
        """
        Get the extra menu items for the plugin menu.
        
        :param request: HttpRequest object
        :param component: CMSPlugin object
        
        :return: list of PluginMenuItem objects
        """
        component_type = 'plugin'

        try:
            id = plugin.id
        except AttributeError:
            return []

        if not plugin.get_plugin_class().allow_children:
            return [plugin_menu_item('export', component_type, id)]

        return [
            plugin_menu_item(operation, component_type, id)
            for operation in ['export', 'import']
        ]

    def get_extra_placeholder_menu_items(request: HttpRequest, placeholder: PlaceholderReference) -> List[PluginMenuItem]:
        """
        Get the extra menu items for the placeholder menu.

        :param request: HttpRequest object
        :param component: PlaceholderReference object

        :return: list of PluginMenuItem objects
        """
        component_type = 'placeholder'

        try:
            id = placeholder.id
        except AttributeError:
            return []

        return [
            plugin_menu_item(operation, component_type, id)
            for operation in ['export', 'import']
        ]


def plugin_menu_item(operation: Literal['export', 'import'], component_type: Literal['plugin', 'placeholder'], id: str) -> PluginMenuItem:
    """
    Create a PluginMenuItem object for exporting or importing plugins.

    :param operation: str, 'export' or 'import'
    :param component_type: str, 'plugin' or 'placeholder'
    :param id: int, ID of the component

    :return: PluginMenuItem object
    """

    if operation not in ('export', 'import'):
        raise ValueError("Invalid operation. Operation must be 'export' or 'import'.")

    if component_type not in ('plugin', 'placeholder'):
        raise ValueError("Invalid component type. Component type must be 'plugin' or 'placeholder'.")

    label = f"{operation.capitalize()} Plugins"
    action = "modal" if operation == "import" else "none"
    url = reverse(f"{operation}_component_data",
                  kwargs={"component_type": component_type,
                          "component_id": id})
    return PluginMenuItem(
        label,
        url,
        action=action,
        attributes={
            "icon": operation,
        },
    )
