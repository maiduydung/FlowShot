"""JSON schema that the LLM must return. Defines the workflow structure."""

WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["title", "before", "after", "metrics", "tagline"],
    "properties": {
        "title": {
            "type": "string",
            "description": "Diagram title. Lead with outcome/money saved. E.g. 'How Acme Saves Clients $50K per Quarter'",
        },
        "before": {
            "type": "object",
            "description": "The painful 'before' state — what the manual/broken process looked like",
            "required": ["nodes", "edges"],
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "label", "type"],
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string", "description": "Short label, max 25 chars"},
                            "sublabel": {"type": "string", "description": "Optional detail like '30+ minutes'"},
                            "type": {
                                "type": "string",
                                "enum": ["input", "process", "warning", "danger"],
                                "description": "input=neutral start, process=step, warning=problem, danger=worst outcome",
                            },
                        },
                    },
                    "minItems": 3,
                    "maxItems": 6,
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["from", "to"],
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                        },
                    },
                },
            },
        },
        "after": {
            "type": "object",
            "description": "The 'after' state — the solution, split into logical sections/lanes",
            "required": ["sections"],
            "properties": {
                "sections": {
                    "type": "array",
                    "description": "1-3 horizontal lanes (e.g. 'Data Pipeline', 'Optimization Engine')",
                    "items": {
                        "type": "object",
                        "required": ["label", "nodes", "edges"],
                        "properties": {
                            "label": {"type": "string", "description": "Section name, e.g. 'DATA PIPELINE'"},
                            "nodes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["id", "label", "type"],
                                    "properties": {
                                        "id": {"type": "string"},
                                        "label": {"type": "string", "description": "Short label, max 25 chars"},
                                        "sublabel": {"type": "string", "description": "Optional tech detail"},
                                        "type": {
                                            "type": "string",
                                            "enum": ["input", "process", "output"],
                                            "description": "input=data source, process=action (blue fill), output=result (blue border)",
                                        },
                                    },
                                },
                                "minItems": 2,
                                "maxItems": 6,
                            },
                            "edges": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["from", "to"],
                                    "properties": {
                                        "from": {"type": "string"},
                                        "to": {"type": "string"},
                                        "style": {
                                            "type": "string",
                                            "enum": ["solid", "dashed"],
                                            "description": "solid=direct flow, dashed=background/async connection",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "minItems": 1,
                    "maxItems": 3,
                },
                "crossEdges": {
                    "type": "array",
                    "description": "Edges connecting nodes across different sections",
                    "items": {
                        "type": "object",
                        "required": ["from", "to"],
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "style": {"type": "string", "enum": ["solid", "dashed"]},
                        },
                    },
                },
            },
        },
        "metrics": {
            "type": "array",
            "description": "3-5 key results with punchy numbers",
            "items": {
                "type": "object",
                "required": ["value", "label"],
                "properties": {
                    "value": {"type": "string", "description": "The number, e.g. '30 min', '20%', '~14M'"},
                    "label": {"type": "string", "description": "Short context, e.g. 'to instant quotes'"},
                },
            },
            "minItems": 3,
            "maxItems": 5,
        },
        "tagline": {
            "type": "string",
            "description": "One-liner at the bottom. No dashes or special chars. E.g. 'Zero workflow disruption. Team keeps using their existing tools.'",
        },
    },
}
