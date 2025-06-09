global_fields_schema = {
    "type": "object",
    "required": ["id", "name", "type", "readonly"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "readonly": {"type": "boolean"},
        "description": {"type": "string"},
        "values": {"type": "array"},
    },
    "additionalProperties": True
}
error_schema = {
    "type": "object",
    "required": ["statusCode"],
    "properties": {
        "statusCode": {"type": "integer"},
        "errorMessages": {
            "type": "array",
            "items": {"type": "string"}
        },
        "errors": {
            "type": "object",
            "additionalProperties": True
        }
    },
    "additionalProperties": True
}
