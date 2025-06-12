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

field_by_id_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "readonly": {"type": "boolean"},
        "visible": {"type": "boolean"},
        "schema": {"type": "object"},
        "description": {"type": "string"},
        "options": {},
        "suggest": {},
        "suggestProvider": {},
        "optionsProvider": {},
        "queryProvider": {},
        "order": {},
        "category": {},
        "version": {},
    },
    "required": ["id", "name", "type", "readonly"],
    "additionalProperties": True
}

patch_options_response_schema = {
    "type": "object",
    "required": ["id", "optionsProvider", "version"],
    "properties": {
        "id": {"type": "string"},
        "optionsProvider": {
            "type": "object",
            "required": ["type", "values"],
            "properties": {
                "type": {"type": "string"},
                "values": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"type": "number"}]}
                }
            },
            "additionalProperties": True
        },
        "version": {"type": "integer"}
    },
    "additionalProperties": True
}


category_schema = {
    "type": "object",
    "required": ["id", "name", "version"],
    "properties": {
        "id": {"type": "string"},
        "name": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "ru": {"type": "string"},
                        "en": {"type": "string"}
                    },
                    "additionalProperties": False
                }
            ]
        },
        "self": {"type": "string"},
        "version": {"type": "integer"},
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
        "errors": {"type": "object"}
    },
    "additionalProperties": True
}

