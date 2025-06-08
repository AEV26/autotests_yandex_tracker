ERROR_SCHEMA = {
    "type": "object",
    "required": [],
    "properties": {
        "code": {"type": "string"},
        "message": {"type": "string"},
        "details": {"type": "array"},
        "errorMessages": {"type": "array"},
        "errors": {"type": "object"}
    },
    "additionalProperties": True
}

DELETE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "code": {"type": "string"}
    }
}