UPDATED_COMMENT_SCHEMA = {
    "type": "object",
    "required": ["self", "id", "text", "createdBy", "createdAt", "updatedBy", "updatedAt"],
    "properties": {
        "self": {"type": "string"},
        "id": {"type": "integer"},
        "longId": {"type": "string"},
        "text": {"type": "string"},
        "createdBy": {
            "type": "object",
            "properties": {
                "self": {"type": "string"},
                "id": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "updatedBy": {
            "type": "object",
            "properties": {
                "self": {"type": "string"},
                "id": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "createdAt": {"type": "string"},
        "updatedAt": {"type": "string"},
        "summonees": {"type": "array"},
        "version": {"type": "integer"},
        "type": {"type": "string"},
        "transport": {"type": "string"}
    },
    "additionalProperties": True
}
