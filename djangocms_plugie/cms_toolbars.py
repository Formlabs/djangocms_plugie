from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class PluginImporter(CMSToolbar):
    class Media:
        css = {"all": ("djangocms_plugie/css/import.css",)}
