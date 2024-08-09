import logging

logger = logging.getLogger(__name__)


def handle_special_plugin_fields(plugin_fields, plugin_id, method_map):
    fields = {}
    for field_name, field_value in plugin_fields.items():
        if not is_special_field(field_value):
            fields[field_name] = field_value
            continue

        extra_kwargs = extract_extra_kwargs(field_value, plugin_id)
        value = get_deserialized_value(field_value, method_map, **extra_kwargs)
        fields[field_name] = value

    return fields

def is_special_field(field_value):
    """
    Checks if the field value is a special field that requires deserialization.

    Args:
        field_value: The value of the field.

    Returns:
        bool: True if the field is special, False otherwise.
    """
    return isinstance(field_value, dict) and '_type' in field_value

def extract_extra_kwargs(field_value, plugin_id):
    """
    Extracts extra keyword arguments from the field value for deserialization.

    Args:
        field_value (dict): The value of the field.
        plugin_id (int): The ID of the plugin.

    Returns:
        dict: The extracted keyword arguments.
    """
    kwargs = {
        key: value for key, value in field_value.items()
        if key.startswith('_') and key not in ['_type']
    }
    kwargs['_plugin_id'] = plugin_id
    return kwargs 

def get_deserialized_value(field_value, method_map, **kwargs):
    value_type = field_value['_type']
    serialize_method = method_map.get(value_type)
    if serialize_method is None:
        raise ValueError(f'No deserialize method found for type "{value_type}"')
    try:
        return serialize_method(**kwargs)
    except NotImplementedError as e:
        msg = f'Error deserializing type "{value_type}": {e}'
        logger.error(msg)
        raise NotImplementedError(msg)
