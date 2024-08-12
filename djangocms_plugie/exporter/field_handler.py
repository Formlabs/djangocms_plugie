from cms.models import CMSPlugin
from djangocms_plugie.config import Config


class FieldHandler:
    def __init__(self):
        self.skip_fields = Config().get_skip_fields()
        self.meta_fields = self._get_meta_field_names()

    def _get_meta_field_names(self):
        return [
            field.name for field in CMSPlugin._meta.fields
            if field.name not in self.skip_fields
        ]

    def get_non_meta_fields(self, downcasted_obj):
        all_fields = [field.name for field in downcasted_obj._meta.get_fields()]

        exclude_fields = set(self.meta_fields + self.skip_fields)
        return [field for field in all_fields if field not in exclude_fields]

    def serialize_fields(self, downcasted_obj, fields, serialize_value):
        return {
            field: serialize_value(downcasted_obj, field)
            for field in fields if hasattr(downcasted_obj, field)
        }
