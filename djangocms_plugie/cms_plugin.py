from cms.plugin_base import CMSPluginBase, PluginMenuItem
from cms.plugin_pool import plugin_pool
from django.urls import reverse


@plugin_pool.register_plugin
class Plugie(CMSPluginBase):
    system = True
    render_plugin = False

    def get_extra_plugin_menu_items(request, component):
        component_type = 'plugin'

        try:
            id = component.id
        except AttributeError:
            return []

        if not component.get_plugin_class().allow_children:
            return [plugin_menu_item('export', component_type, id)]

        return [
            plugin_menu_item(operation, component_type, id)
            for operation in ['export', 'import']
        ]

    def get_extra_placeholder_menu_items(request, component):
        component_type = 'placeholder'

        try:
            id = component.id
        except AttributeError:
            return []

        return [
            plugin_menu_item(operation, component_type, id)
            for operation in ['export', 'import']
        ]


def plugin_menu_item(operation, component_type, id):

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
