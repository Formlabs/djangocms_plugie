from djangocms_plugie.methods.method_base import MethodBase


class ParentRelatedFieldSerializer(MethodBase):
    type_names = ['_parent_related_field']

    @staticmethod
    def serialize():
        return {
            "_type": "_parent_related_field"
        }

    @staticmethod
    def deserialize(**kwargs):
        plugin_id = kwargs.get('_plugin_id', None)
        return plugin_id


class DefaultSerializer(MethodBase):
    type_names = ['str', 'int', 'bool', 'safetext', 'float']

    @staticmethod
    def serialize(value):
        return value


class ToStringSerializer(MethodBase):
    type_names = ['uuid', 'decimal']

    @staticmethod
    def serialize(value):
        return str(value)


class DateTimeSerializer(MethodBase):
    type_names = ['datetime']

    @staticmethod
    def serialize(value):
        return int(value.timestamp())


class NoneSerializer(MethodBase):
    type_names = ['nonetype']

    @staticmethod
    def serialize(value):
        return None


class CMSPluginSerializer(MethodBase):
    type_names = ['cmsplugin']

    @staticmethod
    def serialize(value):
        return value.id
