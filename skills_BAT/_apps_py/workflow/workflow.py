"""Tool for managing and executing workflows."""

import json
from typing import Any, Dict, List, Optional
from loguru import logger
from caiocore.agent.tools.base import Tool

class WorkflowTool(Tool):
    """
    Tool to define and execute structured workflows.
    
    Workflows are sequences of steps (tool calls, LLM prompt, notifications).
    """
    
    def __init__(self, engine: Any):
        self.engine = engine

    @property
    def name(self) -> str:
        return "workflow"

    @property
    def description(self) -> str:
        return (
            "Define and execute a structured workflow (pipeline). "
            "Use this for multi-step processes like 'Extract -> Analyze -> Report'. "
            "Pass the workflow definition as a JSON object with 'name' and 'steps' list."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Descriptive name for the workflow"
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Step ID (used for template referencing)"},
                            "action": {"type": "string", "enum": ["tool", "llm", "notify", "wait"]},
                            "tool": {"type": "string", "description": "Tool name if action is 'tool'"},
                            "args": {"type": "object", "description": "Arguments for tool or notify"},
                            "prompt": {"type": "string", "description": "LLM prompt if action is 'llm' (supports {{step.output}} templates)"},
                            "critical": {"type": "boolean", "description": "Whether to abort on failure (default: true)"}
                        },
                        "required": ["name", "action"]
                    }
                }
            },
            "required": ["name", "steps"]
        }

    async def execute(self, name: str, steps: List[Dict[str, Any]], **kwargs: Any) -> str:
        """Execute the workflow."""
        import uuid
        workflow_id = str(uuid.uuid4())[:8]
        definition = {"name": name, "steps": steps}
        
        # Log to parent tracing if available
        logger.info("WorkflowTool: Triggering workflow '{}' (id: {})", name, workflow_id)
        
        try:
            result_context = await self.engine.execute(workflow_id, definition)
            
            # Extract final results for reporting
            report = f"Workflow '{name}' completed.\n"
            for step in steps:
                s_name = step["name"]
                if s_name in result_context:
                    out = result_context[s_name].get("output")
                    if out:
                        report += f"- {s_name}: {str(out)[:100]}...\n"
            
            return report
        except Exception as e:
            return f"Workflow execution failed: {str(e)}"
