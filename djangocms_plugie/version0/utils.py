def handle_special_plugin_fields(plugin_fields, plugin_id, method_map):
    fields = {}
    for field_name, field_value in plugin_fields.items():
        if not isinstance(field_value, dict):
            fields[field_name] = field_value
            continue

        if '_type' not in field_value or '_data' not in field_value:
            fields[field_name] = field_value
            continue

        extra_kwargs = {
            key: value for key, value in field_value.items()
            if key.startswith('_')
            and key not in ['_type', '_data']
        }
        extra_kwargs['_plugin_id'] = plugin_id
        value = get_deserialized_value(field_value, method_map, **extra_kwargs)
        fields[field_name] = value

    return fields


def get_deserialized_value(field_value, method_map, **extra_kwargs):
    value_type = field_value['_type']
    value = field_value['_data']
    serialize_method = method_map.get(value_type)
    if serialize_method is not None:
        return serialize_method(value, **extra_kwargs)
    raise ValueError(f'No serialize method found for {value_type}')
