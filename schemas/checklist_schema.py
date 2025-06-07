# schemas/checklist_schema.py

checklist_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "text", "checked"],  # assignee не обязателен
        "properties": {
            "id": {"type": "string"},
            "text": {"type": "string"},
            "checked": {"type": "boolean"},
            "assignee": {
                "oneOf": [
                    {"type": "null"},
                    {
                        "type": "object",
                        "required": ["id", "display"],
                        "properties": {
                            "id": {"type": ["string", "number"]},
                            "display": {"type": "string"},
                        },
                        "additionalProperties": True
                    }
                ]
            }
        },
        "additionalProperties": True
    }
}

error_schema = {
    "type": "object",
    "required": ["errorMessages", "statusCode"],
    "properties": {
        "errorMessages": {
            "type": "array",
            "items": {"type": "string"}
        },
        "errors": {"type": "object"},
        "statusCode": {"type": "number"}
    },
    "additionalProperties": True
}
