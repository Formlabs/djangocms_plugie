from django.conf.urls import url
from djangocms_plugie.views import export_component_data, import_component_data


export_url = (
    r'^export_(?P<component_type>plugin|placeholder)/(?P<component_id>.+)/'
)
import_url = (
    r'^import_(?P<component_type>plugin|placeholder)/(?P<component_id>.+)/'
)

urlpatterns = [
    url(
        export_url,
        export_component_data,
        name='export_component_data'
    ),
    url(
        import_url,
        import_component_data,
        name='import_component_data'
    ),
]
