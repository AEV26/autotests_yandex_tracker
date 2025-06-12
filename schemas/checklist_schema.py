

checklist_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "text", "checked"],
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
    "properties": {
        "errorMessages": {
            "type": "array",
            "items": {"type": "string"}
        },
        "errors": {
            "type": "object"
        },
        "statusCode": {
            "type": ["number", "integer"]
        },
        "message": {
            "type": "string"
        },
        "error": {
            "type": "string"
        }
    },
    "additionalProperties": True
}

checklist_item_schema = {
    "type": "object",
    "required": ["id", "text", "checked", "createdAt", "entityType"],
    "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "checked": {"type": "boolean"},
        "assignee": {"type": ["object", "null"]},
        "createdAt": {"type": "string"},
        "entityType": {"type": "string"},
    }
}


checklist_item_response_schema = {
    "type": "object",
    "required": ["id", "text", "checked"],
    "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "checked": {"type": "boolean"},
        "checklistItemType": {"type": "string"},
        "assignee": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "required": ["id", "display"],
                    "properties": {
                        "id": {"type": ["string", "number"]},
                        "display": {"type": "string"}
                    },
                    "additionalProperties": True
                }
            ]
        },
        "deadline": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "deadlineType": {"type": "string"},
                        "isExceeded": {"type": "boolean"}
                    },
                    "additionalProperties": True
                }
            ]
        }
    },
    "additionalProperties": True
}

