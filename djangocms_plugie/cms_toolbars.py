from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class PlugieToolbar(CMSToolbar):
    """ Add the import and export icons to the plugin and placeholder menu context. """
    class Media:
        css = {"all": ("djangocms_plugie/css/import.css",)}
