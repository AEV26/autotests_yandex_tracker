COMMENT_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["self", "id", "longId", "text", "createdBy"],
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
            "createdAt": {"type": "string"},
            "updatedAt": {"type": "string"}
        }
    }
}