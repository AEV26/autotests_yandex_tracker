PROJECT_COMMENTS_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["self", "id", "text", "createdBy", "createdAt"],
        "properties": {
            "self": {"type": "string"},
            "id": {"type": "integer"},
            "longId": {"type": "string"},
            "text": {"type": "string"},
            "textHtml": {"type": "string"},
            "attachments": {"type": "array"},
            "createdBy": {
                "type": "object",
                "properties": {
                    "self": {"type": "string"},
                    "id": {"type": "string"},
                    "display": {"type": "string"},
                    "cloudUid": {"type": "string"},
                    "passportUid": {"type": "integer"}
                }
            },
            "updatedBy": {"type": "object"},
            "createdAt": {"type": "string"},
            "updatedAt": {"type": "string"},
            "summonees": {"type": "array"},
            "version": {"type": "integer"},
            "type": {"type": "string"},
            "transport": {"type": "string"},
            "usersReacted": {"type": "object"},
            "reactionsCount": {"type": "object"},
            "ownReactions": {"type": "array"}
        },
        "additionalProperties": True
    }
}
