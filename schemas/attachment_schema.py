ATTACHMENT_SCHEMA = {
    "type": "object",
    "required": ["self", "id", "name", "size", "createdAt"],
    "properties": {
        "self": {"type": "string"},
        "id": {"type": "string"},
        "name": {"type": "string"},
        "size": {"type": "integer"},
        "createdAt": {"type": "string"},
        "createdBy": {
            "type": "object",
            "required": ["self", "id", "display"],
            "properties": {
                "self": {"type": "string"},
                "id": {"type": "string"},
                "display": {"type": "string"}
            }
        }
    }
}

ATTACHMENT_LIST_SCHEMA = {
    "type": "array",
    "items": ATTACHMENT_SCHEMA
}