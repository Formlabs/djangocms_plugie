import json
from cms.models import CMSPlugin
from django.contrib import messages
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from djangocms_plugie.exporter import Exporter
from djangocms_plugie.forms import PluginImporterForm, ImportForm


@csrf_exempt
def export_component_data(request, component_type, component_id):

    plugin_tree = get_plugin_tree(component_type, component_id)

    serializer = Exporter()
    version = serializer.version
    all_plugins = serializer.serialize_plugins(plugin_tree)
    filename = 'plugins.json'

    data = {
        'version': version,
        'all_plugins': all_plugins,
    }

    messages.success(request, 'Plugin tree exported successfully!')

    response = HttpResponse(json.dumps(data, indent=4, sort_keys=True),
                            content_type="application/json")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


def get_plugin_tree(component_type, component_id):

    if not component_type or not component_id:
        raise ValueError('Component type and ID must be provided.')

    filter_criteria = {'id': component_id} if component_type == 'plugin' else {'placeholder_id': component_id}
    parent_queryset = CMSPlugin.objects.filter(**filter_criteria)
    descendants = parent_queryset[0].get_descendants() if component_type == 'plugin' else CMSPlugin.objects.none()
    plugin_tree = parent_queryset | descendants

    return plugin_tree


def import_component_data(request, component_type, component_id):

    new_form = PluginImporterForm({component_type: component_id})

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
    # TODO: refactor these errors
    except (TypeError, IntegrityError, ValueError, ImportError, AttributeError) as e:
        import_form.add_error("import_file", str(e))
        return render(request, "djangocms_plugie/import_plugins.html", context)

    # TODO: Fix this redirect. It should close the modal and refresh the page.
    return redirect('admin:index')
