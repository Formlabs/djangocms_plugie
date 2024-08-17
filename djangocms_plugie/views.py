import json
from typing import Literal
from cms.models import CMSPlugin
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from djangocms_plugie.exporter import Exporter
from djangocms_plugie.forms import PluginOrPlaceholderSelectionForm, ImportForm


@csrf_exempt
def export_component_data(request: HttpRequest, component_type: Literal['plugin', 'placeholder'], component_id: int) -> HttpResponse:
    """"
    Export the plugin tree of a given component to a JSON file.
    
    :param request: HttpRequest object
    :param component_type: str, 'plugin' or 'placeholder'
    :param component_id: int, ID of the component

    :return: HttpResponse object
    """

    plugin_tree = get_plugin_tree(component_type, component_id)

    try:
        serializer = Exporter()
        version = serializer.version
        all_plugins = serializer.serialize_plugins(plugin_tree)
        filename = 'plugins.json'

        data = {
            'version': version,
            'all_plugins': all_plugins,
        }

        response = HttpResponse(json.dumps(data, indent=4, sort_keys=True),
                                content_type="application/json")
    except Exception as e:
        filename = 'error.txt'
        response = HttpResponse(str(e), content_type="text/plain")

    finally:
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


def get_plugin_tree(component_type: Literal['plugin', 'placeholder'], component_id: int) -> QuerySet:
    """
    Get the plugin tree of a given component.

    :param component_type: str, 'plugin' or 'placeholder'
    :param component_id: int, ID of the component

    :return: QuerySet object of CMSPlugin
    """

    if not component_type or not component_id:
        raise ValueError('Component type and ID must be provided.')

    filter_criteria = {'id': component_id} if component_type == 'plugin' else {'placeholder_id': component_id}
    parent_queryset = CMSPlugin.objects.filter(**filter_criteria)
    descendants = parent_queryset[0].get_descendants() if component_type == 'plugin' else CMSPlugin.objects.none()
    plugin_tree = parent_queryset | descendants

    return plugin_tree


def import_component_data(request: HttpRequest, component_type: Literal['plugin', 'placeholder'], component_id: int) -> HttpResponse:
    """"
    Import the plugin tree from a JSON file to a given component.

    :param request: HttpRequest object
    :param component_type: str, 'plugin' or 'placeholder'
    :param component_id: int, ID of the component

    :return: HttpResponse object
    """

    new_form = PluginOrPlaceholderSelectionForm({component_type: component_id})

    if new_form.is_valid():
        initial_data = new_form.cleaned_data
    else:
        initial_data = None

    if request.method == "GET" and not new_form.is_valid():
        return HttpResponseBadRequest("Form received unexpected values.")

    import_form = ImportForm(
        data=request.POST or None,
        files=request.FILES or None,
        initial=initial_data,
    )

    context = {
        "form": import_form,
        "has_change_permission": True,
        "is_popup": True,
        "app_label": 'djangocms_plugie',
    }

    if not import_form.is_valid():
        return render(request, "djangocms_plugie/import_plugins.html", context)

    try:
        import_form.run_import()
        messages.success(request, 'Plugin tree imported successfully!')
    except Exception as e:
        import_form.add_error("import_file", str(e))
        return render(request, "djangocms_plugie/import_plugins.html", context)

    return render(request, "djangocms_plugie/refresh_page.html")
