issue_link_schema = {
    "type": "object",
    "required": ["type", "object", "direction"],
    "properties": {
        "type": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string"}
            },
            "additionalProperties": True
        },
        "object": {
            "type": "object",
            "required": ["key"],
            "properties": {
                "key": {"type": "string"}
            },
            "additionalProperties": True
        },
        "direction": {"type": "string"}
    },
    "additionalProperties": True
}

issue_links_list_schema = {
    "type": "array",
    "items": issue_link_schema
}

issue_links_error_schema = {
    "type": "object",
    "required": ["statusCode"],
    "properties": {
        "errorMessages": {
            "type": "array",
            "items": {"type": "string"}
        },
        "errors": {
            "type": "object",
            "additionalProperties": True
        },
        "statusCode": {"type": "integer"}
    },
    "additionalProperties": True
}
