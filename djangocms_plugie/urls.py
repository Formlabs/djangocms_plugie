from django.conf.urls import url
from djangocms_plugie.views import export_component_data, import_component_data


urlpatterns = [
    url(
        r'^export_(?P<component_type>plugin|placeholder)/(?P<component_id>.+)/',
        export_component_data,
        name='export_component_data'
    ),
    url(
        r'^import_(?P<component_type>plugin|placeholder)/(?P<component_id>.+)/',
        import_component_data,
        name='import_component_data'
    ),
]
