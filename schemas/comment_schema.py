COMMENT_SCHEMA = {
    "type": "object",
    "required": ["self", "id", "longId", "text", "createdBy", "updatedBy", "createdAt", "updatedAt"],
    "properties": {
        "self": {"type": "string"},
        "id": {"type": "integer"},
        "longId": {"type": "string"},
        "text": {"type": "string"},
        "createdBy": {
            "type": "object",
            "required": ["self", "id", "display"],
            "properties": {
                "self": {"type": "string"},
                "id": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "updatedBy": {
            "type": "object",
            "required": ["self", "id", "display"],
            "properties": {
                "self": {"type": "string"},
                "id": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "createdAt": {"type": "string"},
        "updatedAt": {"type": "string"}
    }
}