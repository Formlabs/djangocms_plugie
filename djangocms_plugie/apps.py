from django.apps import AppConfig


class ImportPluginsConfig(AppConfig):
    name = 'djangocms_plugie'
    verbose_name = 'Django CMS Plugins Importer/Exporter'

    def ready(self):
        from djangocms_plugie.cms_plugin import PluginImporter  # noqa
