"""LLM tool schemas and system prompt for intent routing.

Each tool schema describes one backend endpoint. The LLM reads these
descriptions to decide which tool to call for a user's question.
Quality of descriptions directly affects routing accuracy.
"""

from services.api_client import APIClient

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List all items (labs, tasks, etc.) available in the LMS. Use this to discover what labs exist before querying lab-specific data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "List enrolled students and their groups. Use to answer questions about enrollment, how many students are in the course, or group membership.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Optional lab identifier to filter learners by lab.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution in 4 buckets for a lab. Use to show how many students scored in each range (e.g., 0-25%, 25-50%, 50-75%, 75-100%).",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use to compare task difficulty within a lab or show which tasks students struggle with.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission counts per day for a lab. Use to show activity over time, peak submission days, or submission patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use to compare groups, find the best or worst performing group, or see group-level statistics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners ranked by score for a lab. Use to show leaderboards or identify highest-performing students.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, e.g. 5 or 10.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get the completion rate percentage for a lab. Use to answer questions about what fraction of students completed a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger a data refresh from the autochecker. Use when the user asks to sync, refresh, or update data from the autochecker.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "You are a helpful assistant for a Learning Management System. "
    "Users ask questions about labs, scores, pass rates, groups, and students. "
    "You have access to tools that fetch data from the backend. "
    "ALWAYS use tools to answer questions — never guess or make up data. "
    "If a question requires data from multiple labs, call the tool for each lab and compare. "
    "For greetings or ambiguous messages, respond directly without tools. "
    "If the user's message is unclear, politely ask what they'd like to know and list your capabilities. "
    "Keep responses concise and include relevant numbers from the data."
)


def build_tool_callbacks(client: APIClient) -> dict:
    """Build a map of tool name -> callback function.

    Each callback calls the appropriate API endpoint on the APIClient.
    """
    return {
        "get_items": lambda: client.get("/items/"),
        "get_learners": lambda lab="": client.get(
            f"/learners/?lab={lab}" if lab else "/learners/"
        ),
        "get_scores": lambda lab: client.get(f"/analytics/scores?lab={lab}"),
        "get_pass_rates": lambda lab: client.get(f"/analytics/pass-rates?lab={lab}"),
        "get_timeline": lambda lab: client.get(f"/analytics/timeline?lab={lab}"),
        "get_groups": lambda lab: client.get(f"/analytics/groups?lab={lab}"),
        "get_top_learners": lambda lab="", limit=10: client.get(
            f"/analytics/top-learners?lab={lab}&limit={limit}"
            if lab
            else f"/analytics/top-learners?limit={limit}"
        ),
        "get_completion_rate": lambda lab: client.get(
            f"/analytics/completion-rate?lab={lab}"
        ),
        "trigger_sync": lambda: client.post("/pipeline/sync"),
    }
