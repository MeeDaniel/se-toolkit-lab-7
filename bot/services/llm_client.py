"""
LLM client with tool-calling support.

Implements the same tool-use pattern from Lab 6:
1. Define tool schemas (function descriptions)
2. Send user message + tools to LLM
3. LLM returns tool calls
4. Execute tools, feed results back to LLM
5. LLM produces final answer
"""

import json
import sys
from typing import Any, Callable

import httpx


# System prompt that instructs the LLM to use tools
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS).
You have access to tools that let you query data about labs, students, scores, and analytics.

When the user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Use the tool results to formulate your answer

If the user's message is unclear or ambiguous, ask for clarification.
If the user greets you or asks something you can't help with, respond politely and explain what you can do.

Always use tools to get accurate data before answering questions about labs, scores, or students.
"""


def get_tool_schemas() -> list[dict[str, Any]]:
    """
    Define all 9 backend endpoints as LLM tools.
    
    The LLM reads these descriptions to decide which tool to call.
    Clear, specific descriptions are critical for correct tool use.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get all items (labs and tasks) from the LMS. Use this to list available labs or find lab identifiers.",
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
                "description": "Get all enrolled learners and their group assignments. Use this to find student names, IDs, or group memberships.",
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
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed across ranges.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average pass rates and attempt counts for a specific lab. Use this to compare task difficulty or find the hardest/easiest task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline (submissions per day) for a specific lab. Use this to see when students submitted work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a specific lab. Use this to compare group performance or find the best/worst performing group.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a specific lab. Use this to create leaderboards or find high-performing students.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, e.g. 5, 10",
                        },
                    },
                    "required": ["lab", "limit"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a specific lab. Use this to see what percentage of students completed the lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh the LMS data. Use this when the user asks to update or refresh data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


class LLMClient:
    """Client for LLM API with tool-calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _debug(self, message: str):
        """Print debug message to stderr (visible in --test mode)."""
        print(message, file=sys.stderr)

    def _call_llm(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """
        Make a chat completion request to the LLM.
        
        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions
            
        Returns:
            LLM response as a dict
        """
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def _execute_tool(
        self, tool_name: str, arguments: dict[str, Any], api_client: Any
    ) -> Any:
        """
        Execute a tool by calling the corresponding API method.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            api_client: LMSAPIClient instance
            
        Returns:
            Tool result (API response)
        """
        if tool_name == "get_items":
            return api_client.get_items()
        elif tool_name == "get_learners":
            return api_client.get_learners()
        elif tool_name == "get_scores":
            return api_client.get_scores(arguments.get("lab", ""))
        elif tool_name == "get_pass_rates":
            return api_client.get_pass_rates(arguments.get("lab", ""))
        elif tool_name == "get_timeline":
            return api_client.get_timeline(arguments.get("lab", ""))
        elif tool_name == "get_groups":
            return api_client.get_groups(arguments.get("lab", ""))
        elif tool_name == "get_top_learners":
            return api_client.get_top_learners(
                arguments.get("lab", ""), arguments.get("limit", 5)
            )
        elif tool_name == "get_completion_rate":
            return api_client.get_completion_rate(arguments.get("lab", ""))
        elif tool_name == "trigger_sync":
            return api_client.trigger_sync()
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def route(
        self, user_message: str, api_client: Any, max_iterations: int = 5
    ) -> str:
        """
        Route a user message through the LLM tool-calling loop.
        
        This is the core intent routing logic:
        1. Send user message + tool definitions to LLM
        2. LLM decides which tool(s) to call
        3. Execute tools, feed results back to LLM
        4. LLM produces final answer
        
        Args:
            user_message: The user's input message
            api_client: LMSAPIClient instance for executing tools
            max_iterations: Maximum tool-calling iterations
            
        Returns:
            Final response text
        """
        tools = get_tool_schemas()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        for iteration in range(max_iterations):
            # Call LLM with current conversation state
            response = self._call_llm(messages, tools)
            choice = response["choices"][0]
            assistant_message = choice["message"]

            # Add assistant's message to conversation
            messages.append(assistant_message)

            # Check if LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])
            if not tool_calls:
                # No tool calls - LLM is ready to give final answer
                return assistant_message.get("content", "I don't have enough information to answer that.")

            # Execute each tool call
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = json.loads(function["arguments"])

                self._debug(f"[tool] LLM called: {tool_name}({tool_args})")

                try:
                    result = self._execute_tool(tool_name, tool_args, api_client)
                    tool_results.append(result)
                    self._debug(f"[tool] Result: {len(str(result))} chars")
                except Exception as e:
                    self._debug(f"[tool] Error: {e}")
                    tool_results.append({"error": str(e)})

            # Feed tool results back to LLM
            self._debug(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(tool_results),
                }
            )

        # If we reach max iterations, return what we have
        return "I'm still working on that. Let me try again."


def create_llm_client(api_key: str, base_url: str, model: str) -> LLMClient:
    """Factory function to create an LLM client."""
    return LLMClient(api_key, base_url, model)
